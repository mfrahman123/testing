import pandas as pd



def column_names():
    '''Get all column data from relative activity results table produced by R code for HTML use'''
    df = pd.read_csv('relative.csv', index_col=0)

    column_names = []

    for col in df.columns:
        column_names.append(col)

    return column_names


def row_names():
    '''Get all row data from relative activity results table produced by R code for HTML use'''

    df = pd.read_csv('relative.csv', index_col=0)

    row_names = []
    for row in df.index:
        row_list = []
        row_list.append(row)
        row = df.loc[row]
        for item in row:
            row_list.append(item)
        row_names.append(row_list)

    return row_names
