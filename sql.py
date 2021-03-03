#data extraction and SQL database for task 1

#Import Statements
import pandas as pd
from cs50 import SQL
import csv

##Retrieve data
def get_important_data():
#get data from url and store content
    try:
        # Extraction of data for Ensembl, Symbol and Family
        url = "http://bioinfo.life.hust.edu.cn/static/AnimalTFDB3/download/Homo_sapiens_TF"
        req = requests.get(url)
        url_content = req.content
        tsv_file1 = open('download1.tsv', 'wb')
        tsv_file1.write(url_content)
        tsv_file1.close()

        #Extraction of data for full name and chromosomal location
        # old_url = 'https://www.genenames.org/cgi-bin/download/custom?col=gd_hgnc_id&col=gd_app_sym&col=gd_app_name&col=gd_pub_chrom_map&col=gd_pub_acc_ids&col=md_ensembl_id&status=Approved&status=Entry%20Withdrawn&hgnc_dbtag=on&order_by=gd_app_sym_sort&format=text&submit=submit'
        new_url = 'https://www.genenames.org/cgi-bin/download/custom?col=gd_hgnc_id&col=gd_app_sym&col=gd_app_name&col=gd_pub_chrom_map&col=md_prot_id&col=md_ensembl_id&status=Approved&status=Entry%20Withdrawn&hgnc_dbtag=on&order_by=gd_app_sym_sort&format=text&submit=submit'
        req2 = requests.get(new_url)
        url_content2 = req2.content
        tsv_file2 = open('download2.tsv', 'wb')
        tsv_file2.write(url_content2)
        tsv_file2.close()

        return 'Data was extracted successfully!'
    except Exception as e:

        return e

#create pandas dataframe from tsv file
htf_df = pd.read_csv('download1.tsv', sep='\t')
htf_df.rename(columns={'Entrez ID':'Entrez_ID'},inplace=True)
#Remove unnecessary columns
htf_df.drop(columns=['Species','Protein','Entrez_ID'],inplace=True)

# create pandas dataframe from tsv file
df1 = pd.read_csv('download2.tsv', sep='\t')
del df1['HGNC ID']
df2= df1.rename(columns = {'Approved symbol': 'Symbol', 'Approved name': 'Protein_name', 'Ensembl ID(supplied by Ensembl)': 'Ensembl'}, inplace = False)


#keep the rows that contain the tf ensembl accession-- 1643 proteins

df3= pd.merge (df2, htf_df, on="Symbol")
df3= df3.rename(columns={'UniProt ID(supplied by UniProt)':'Uniprot'}, inplace = False)


#save the dataframe to a new .tsv file
df3.to_csv("htfUniprot.tsv", sep="\t", index=False)

####create an empty database
open("tranfac.db", "w").close()  

#open the tranfac database
db = SQL("sqlite:///tranfac.db") 

# Create table
db.execute("CREATE TABLE HtfUniprot (Uniprot TEXT NON NULL, Protein_name TEXT NOT NULL, Symbol TEXT NOT NULL, Family TEXT NON NULL, Chromosome TEXT NOT NULL, Ensembl TEXT NOT NULL, PRIMARY KEY (Symbol))")

# Open CSV file
with open("htfUniprot.tsv", "r") as file:

    # Create DictReader
    reader = csv.DictReader(file, delimiter="\t")

    # Iterate over CSV file
    for row in reader:
        Symbol= row['Symbol'].strip().upper()
        Protein_name= row['Protein_name']
        Chromosome= row['Chromosome']
        Uniprot= row['Uniprot'].strip().upper()
        Ensembl= row['Ensembl_x']
        Family=row['Family']

        db.execute("INSERT INTO HtfUniprot (Uniprot, Protein_name , Symbol , Family , Chromosome, Ensembl) VALUES (?, ?, ?, ?, ?, ?)", Uniprot, Protein_name , Symbol , Family , Chromosome, Ensembl)



#Retrieve rows and extract relevant data for subcellular location and function from uniprot database
subcellular_df = pd.read_csv('uniprot.txt', sep='\t')
subcellular_df = subcellular_df.fillna(0)
subcellular_df.drop(columns=['Status', 'Entry name'],inplace=True)
subcellular_df.rename(columns={'Gene names':'Symbol', 'Subcellular location [CC]':'Subcellular_location', 'Function [CC]':'Functions'}, inplace=True)

#get rid of superfluous values
subcellular_df['Subcellular_location']= subcellular_df['Subcellular_location'].str.replace('SUBCELLULAR LOCATION:', '')

subcellular_df['Functions']= subcellular_df['Functions'].str.replace('FUNCTION:', '')

#remove brackets and string within brackets
subcellular_df['Subcellular_location']= subcellular_df['Subcellular_location'].str.replace(r"\{.*\}","")
subcellular_df['Subcellular_location'] = subcellular_df['Subcellular_location'].str.replace('.','')
subcellular_df['Functions']= subcellular_df['Functions'].str.replace(r"\{.*\}","")
subcellular_df['Functions']= subcellular_df['Functions'].str.replace(r"\(.*\)","")
subcellular_df['Functions'] = subcellular_df['Functions'].str.replace('.','')


#only keep values related to TF
df4=(subcellular_df[subcellular_df.Entry.isin(df3.Uniprot)])
print(df4)

#save as .tsv file
df4.to_csv("location.tsv", sep="\t", index=False)

# Create table
db.execute("CREATE TABLE HtfLocation (Uniprot TEXT, Subcellular_location TEXT, Functions TEXT)")

# Open CSV file
with open("location.tsv", "r") as file1:

    # Create DictReader
    reader1 = csv.DictReader(file1, delimiter="\t")
    
    # Iterate over CSV file
    for rows in reader1:
        
      Uniprot= rows['Entry'].strip().upper() 
      Subcellular_location= rows ['Subcellular_location']
      Functions= rows ["Functions"]
      
      db.execute("INSERT INTO HtfLocation (Uniprot, Subcellular_location, Functions) VALUES (?, ?, ?)", Uniprot, Subcellular_location, Functions)
 
#Create indexes for important values
db.execute("CREATE INDEX symbol_index ON HtfUniprot (Symbol);")


#Retrieve all information related to specific symbols this command in sqlite : SELECT * FROM HtfUniprot JOIN HtfLocation ON HtfUniprot.Uniprot = HtfLocation.Uniprot WHERE HtfUniprot.Symbol = "- user inputted symbol- ";
