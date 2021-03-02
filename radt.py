import pandas as pd


#create dataframe of relative activity data from R 
df = pd.read_csv('relative.csv', index_col=0)

#extract column names from relative activity data for html
def column_names():
    column_names = []

    for col in df.columns:
        column_names.append(col)

    return column_names

#extract row items for each row and produce list for html
def row_names():
    row_names = []


    for row in df.index:
        row_list = []
        row_list.append(row)
        row = df.loc[row]
        for item in row:
            row_list.append(item)
        row_names.append(row_list)

    return row_names

