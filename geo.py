import GEOparse

def open_gds(filename):
    gds = GEOparse.get_GEO(filepath="%s" % filename)
    Table = gds.table
    metadata = gds.columns
    Table = Table.drop(columns = 'ID_REF')
    Table = Table[(Table['IDENTIFIER']!='--Control') | (Table['IDENTIFIER']!='control')]
    Table = Table.groupby('IDENTIFIER').mean().reset_index()
    return Table
