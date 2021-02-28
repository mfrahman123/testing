#

#Import Statements
import pandas as pd
import numpy as np
import requests
import gzip
import shutil
import time
from cs50 import SQL
import csv


#open the chembl_28.db database
db = SQL("sqlite:///chembl_28.db")

# Extraction of data for Ensembl, Symbol and Family
url = "http://bioinfo.life.hust.edu.cn/static/AnimalTFDB3/download/Homo_sapiens_TF"
eq = requests.get(url)
url_content = req.content
tsv_file1 = open('download1.tsv', 'wb')
tsv_file1.write(url_content)
tsv_file1.close()

# Create table
db.execute("CREATE TABLE transcription_factors (Symbol VARCHAR2(10), Family VARCHAR2(20), Ensembl VARCHAR2(20), PRIMARY KEY (Symbol))")

#open .tsv file
with open ("download1.tsv") as file:
    # Create DictReader
    reader = csv.DictReader(file, delimiter="\t")
    
    #iterate over the file
    for row in reader: 
        Symbol = row['Symbol'].strip().upper()
        Family = row['Family'].strip().upper()
        Ensembl= row['Ensembl'].strip().upper()
        
        #insert into table
        db.execute("INSERT INTO transcription_factors (Symbol, Family, Ensembl) VALUES (?, ?, ?)", Symbol, Family, Ensembl)




#Extraction of data for full name and chromosomal location
# old_url = 'https://www.genenames.org/cgi-bin/download/custom?col=gd_hgnc_id&col=gd_app_sym&col=gd_app_name&col=gd_pub_chrom_map&col=gd_pub_acc_ids&col=md_ensembl_id&status=Approved&status=Entry%20Withdrawn&hgnc_dbtag=on&order_by=gd_app_sym_sort&format=text&submit=submit'
new_url = 'https://www.genenames.org/cgi-bin/download/custom?col=gd_hgnc_id&col=gd_app_sym&col=gd_app_name&col=gd_pub_chrom_map&col=md_prot_id&col=md_ensembl_id&status=Approved&status=Entry%20Withdrawn&hgnc_dbtag=on&order_by=gd_app_sym_sort&format=text&submit=submit'
req2 = requests.get(new_url)
url_content2 = req2.content
tsv_file2 = open('download2.tsv', 'wb')
tsv_file2.write(url_content2)
tsv_file2.close()

# Create table
db.execute("CREATE TABLE chromosomal_location ( Symbol VARCHAR2(10), Protein_name VARCHAR2(30), Chromosome VARCHAR2(20), Uniprot_ID VARCHAR2(10))")

#open .tsv file
with open ("download2.tsv") as file1:
    # Create DictReader
    reader1 = csv.DictReader(file1, delimiter="\t")
    
    #iterate over the file
    for rows in reader1: 
        Symbol= rows['Approved symbol']
        Protein_name = rows['Approved name']
        Chromosome= rows['Chromosome']
        Uniprot_ID= rows['UniProt ID(supplied by UniProt)'].strip().upper()
        
        
        #insert into table
        db.execute("INSERT INTO chromosomal_location (Symbol, Protein_name, Chromosome, Uniprot_ID) VALUES (?, ?, ?, ?)", Symbol, Protein_name, Chromosome, Uniprot_ID)
        
        db.execute("DELETE FROM chromosomal_location WHERE Symbol NOT IN (SELECT Symbol from transcription_factors)")
    
    
        
#open file containing interactions between genes and drugs downloaded from https://www.dgidb.org/downloads
inte_df= pd.read_csv ('interactions.tsv',sep='\t')
inte_df.rename(columns={'gene_name':'Symbol'},inplace=True)

#Only keep the genes that are transcription factors
Uniprot_df= pd.read_csv ('download1.tsv',sep='\t')
df2= inte_df[inte_df["Symbol"].isin(Uniprot_df["Symbol"])]

df2.to_csv("HTFgenedruginteraction.tsv", sep="\t", index=False)

# Create table
db.execute("CREATE TABLE HtfGandD (Symbol TEXT NOT NULL, interaction_types TEXT, drug_name TEXT NOT NULL, drug_concept_id TEXT NOT NULL)")

# Open CSV file
with open("HTFgenedruginteraction.tsv", "r") as file:

    # Create DictReader
    reader = csv.DictReader(file, delimiter="\t")

    # Iterate over CSV file
    for row in reader:
        Symbol= row['Symbol'].strip().upper()
        interaction_types= row['interaction_types']
        drug_name= row['drug_name'].strip()
        drug_concept_id= row['drug_concept_id'].replace("chembl:","")
        
#insert values in the table        
        db.execute("INSERT INTO HtfGandD (Symbol, interaction_types, drug_name, drug_concept_id) VALUES ( ?, ?, ?, ?)", Symbol, interaction_types, drug_name, drug_concept_id)


#Retrieve rows and extract relevant data for subcellular location and function from uniprot database
subcellular_df = pd.read_csv('uniprot.txt',sep='\t')
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
subcellular_df['Functions'] = subcellular_df['Functions'].str.replace('.','-')


#save as .tsv file
subcellular_df.to_csv("location.tsv", sep="\t", index=False)


    
# Create table
db.execute("CREATE TABLE HtfLocation (Uniprot TEXT, Subcellular_location TEXT, Functions TEXT)")

# Open CSV file
with open("location.tsv", "r") as file10:

    # Create DictReader
    reader10 = csv.DictReader(file10, delimiter="\t")
    
    # Iterate over CSV file
    for rowss in reader10:
        
      Uniprot= rowss['Entry'].strip().upper() 
      Subcellular_location= rowss ['Subcellular_location']
      Functions= rowss ["Functions"]
      
     #insert values in the table, and delete che values that are not in the table containing the trasncription factors 
      db.execute("INSERT INTO HtfLocation (Uniprot, Subcellular_location, Functions) VALUES (?, ?, ?)", Uniprot, Subcellular_location, Functions)
      db.execute("DELETE FROM HtfLocation WHERE Uniprot NOT IN (SELECT Uniprot_ID FROM chromosomal_location")
    
