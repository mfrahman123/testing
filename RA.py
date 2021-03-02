#Import relevant packages
import GEOparse
import pandas as pd

#create dataframe from CHIP-SEQ data for all human transcription factors
target_matrix = pd.read_csv('tf_matrix.tsv', sep='\t', index_col=0)
#create a list for gene names
targets1 = list(target_matrix.index)

#parse the GDS data that user uploads and clean it up to only include relevant information. 
#remove control data
def open_gds(filename):
    gds = GEOparse.get_GEO(filepath="%s" % filename)
    Table = gds.table
    metadata = gds.columns
    Table = Table.drop(columns='ID_REF')
    Table = Table[(Table['IDENTIFIER'] != '--Control') | (Table['IDENTIFIER'] != 'control')]
    Table = Table.groupby("IDENTIFIER").mean().reset_index()
    return Table

#create matrix for gene expression data of equal dimensions to connec data for plsgenomics package use in R
def ge_data(filename):
    data = open_gds(filename)
    data = data.loc[data['IDENTIFIER'].isin(targets1)]
    data = data.set_index('IDENTIFIER')
    return data

#create matrix for connec data of equal dimensions to gene expression data for plsgenomics package use in R
def connec_data(ge_data):
    connec = target_matrix.loc[target_matrix.index.isin(list(ge_data.index))]


    return connec
