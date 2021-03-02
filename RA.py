
import GEOparse
import pandas as pd

target_matrix = pd.read_csv('tf_matrix.csv', sep=',', index_col=0)
targets1 = list(target_matrix.index)


def open_gds(filename):
    gds = GEOparse.get_GEO(filepath="%s" % filename)


    Table = gds.table
    metadata = gds.columns
    Table = Table.drop(columns='ID_REF')
    Table = Table[(Table['IDENTIFIER'] != '--Control') | (Table['IDENTIFIER'] != 'control')]
    Table = Table.groupby("IDENTIFIER").mean().reset_index()
    return Table


def ge_data(filename):
    data = open_gds(filename)


    data = data.loc[data['IDENTIFIER'].isin(targets1)]
    data = data.set_index('IDENTIFIER')
    return data


def connec_data(ge_data):
    connec = target_matrix.loc[target_matrix.index.isin(list(ge_data.index))]


    return connec

testge=ge_data('GDS859.soft.gz')
connec = connec_data(testge)
testge.to_csv('ge_data.csv')
connec.to_csv('connec_data.csv')
