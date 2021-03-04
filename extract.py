#Import Statements
import pandas as pd
import numpy as np
import requests
import gzip
import shutil
import time
from cs50 import SQL
import csv

def get_important_data():
#get data from url and store content
''' Get data for Ensembl, Symbol, Family, full name and chromosomal location'''
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

# def df_for_all_genes():
#     with open('genes.txt', 'r') as FILE:
#             lines = FILE.readlines()
#             list1 = []
#             list2 = []
#             location_df = pd.read_csv('download2.tsv', sep='\t')
#             location_df.drop(columns=['HGNC ID'],inplace=True)
#             location_df.index.name = 'ID'
#             location_df.rename(columns={'Approved symbol':'Symbol', 'Approved name': 'Full_name',
#                                         'Ensembl ID(supplied by Ensembl)' : 'Ensembl', 'UniProt ID(supplied by UniProt)': 'Uniprot'},inplace=True)

#             for i in lines:
#                 i = i.replace('\n','')
#                 list1.append(i)
#             for j in list1:
#                 indx_val = location_df.index.values[location_df.Symbol == j].tolist()
#                 for t in range(len(indx_val)):
#                     list2.append(indx_val[t])

#             df1 = location_df.loc[list2]
#             df1.fillna(0)

#             return df1

# def all_data_to_dict():
#     try:

#         get_important_data()

#         #create pandas dataframe from tsv file
#         htf_df = pd.read_csv('download1.tsv',sep='\t')
#         htf_df.rename(columns={'Entrez ID':'Entrez_ID'},inplace=True)

#         #Remove unnecessary columns
#         htf_df.drop(columns=['Species','Protein','Entrez_ID','Ensembl'],inplace=True)

#         #provide index name
#         htf_df.index.name = 'ID'

#         dict10 = {}
#         #Retrieve rows and extract relevant data for subcellular location and function from uniprot database
#         subcellular_df = pd.read_csv('uniprot.txt',sep='\t')
#         subcellular_df = subcellular_df.fillna(0)
#         subcellular_df.drop(columns=['Status'],inplace=True)
#         subcellular_df.rename(columns={'Entry name':'Entry_name', 'Subcellular location [CC]':'SC', 'Function [CC]':'F'}, inplace=True)

#         df1 = df_for_all_genes()
#         uniprot_stuff = df1.Uniprot.values
#         symbol_stuff = df1.Symbol.values

#         for i,z in zip(uniprot_stuff,symbol_stuff):
#             idx_loc = htf_df.loc[htf_df.Symbol == z]
#             if i != 0:
#                 row_data = subcellular_df.loc[subcellular_df.Entry == i]
#                 subcell_loc = row_data.SC.values
#                 func_data = row_data.F.values
#                 for num in range(len(subcell_loc)):
#                     if subcell_loc != 0:
#                         subcell_loc = subcell_loc[num]
#                     else:
#                         subcell_loc = 'Not found'
#                     if func_data != 0:
#                         func_data = func_data[num]
#                     else:
#                         func_data = 'Not found'
#                     try:
#                         family_num = idx_loc.Family.values
#                         family = family_num[num]
#                     except:
#                         family = 'Not found'
#                     full_name = df1.Full_name[df1.Symbol == z].values[num]
#                     chr_loc = df1.Chromosome[df1.Symbol == z].values[num]
#                     ensembl = df1.Ensembl[df1.Symbol == z].values[num]
#                     dict10[z] = {'Full_Name':full_name,'Symbol':z,'Uniprot': i, 'Family':family, 'Ensembl':ensembl, 'Chr_loc':chr_loc, 'Subcell':subcell_loc, 'Func':func_data, }
#                     break

#             else:
#                 No_data = 'No data found'
#                 for num2 in range(3):
#                     full_name = df1.Full_name[df1.Symbol == z].values[num2]
#                     chr_loc = df1.Chromosome[df1.Symbol == z].values[num2]
#                     ensembl = df1.Ensembl[df1.Symbol == z].values[num2]
#                     try:
#                         family_num = idx_loc.Family.values
#                         family = family_num[num]
#                     except:
#                         family = 'Not found'
#                     dict10[z] = {'Full_Name':full_name,'Symbol':z,'Uniprot':'Not found','Family':family, 'Ensembl':ensembl, 'Chrom_loc':chr_loc, 'Subcell':No_data, 'Func':No_data, }
#                     break

#         return dict10

#     except Exception as e:
#         return e


def get_symbols():
    
    ''' get all current existing htf gene symbol data and make into a list'''

    db = SQL("sqlite:///tranfac.db") 

    symbol_data = db.execute(''' SELECT Symbol FROM HtfUniprot''')
    symbol_list = []
    for x in symbol_data:
        symbol_list.append(x['Symbol'])

    return symbol_list
