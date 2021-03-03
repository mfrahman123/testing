#Import Statements
import pandas as pd
import numpy as np
import requests
import gzip
import shutil

def get_htf_target_data(tf_gene_symbol):

    '''Gets data for which genes the transcription factors target with some additional info.

    Key Arguments:

    tf_gene_symbol --- Gene Symbol of valid human transcription factor '''

    dict1 = {}

    try:
        #Extraction of data for target genes.
        target_url = 'http://bioinfo.life.hust.edu.cn/hTFtarget/static/hTFtarget/tmp_files/targets/' + tf_gene_symbol + '.target.txt.gz' 
        r2 = requests.get(target_url, stream=True)

        with open('../target.txt.gz', 'wb') as f:
            f.write(r2.content)
        #decompress gz file and convert to txt file
        with gzip.open('../target.txt.gz', 'rb') as f_in:
            with open('../target.txt', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        #create pandas dataframe from txt file
        target_df = pd.read_csv('../target.txt', sep ='\t')

        #provide index name and appropriate column names
        target_df.index.name = 'ID'
        target_df.rename(columns={'TF_name':'Symbol', 'target_id':'Target_Ensembl',
        'target_name':'Target_Name', 'target_synonyms':'Target_Synonyms'},inplace=True)

        a = np.ndarray.tolist(target_df.Target_Ensembl.values)
        b = np.ndarray.tolist(target_df.Target_Name.values)
        c = np.ndarray.tolist(target_df.Target_Synonyms.values)

        i = 0

        for x in list(zip(b,a,c)) :

            i += 1
            str_i = str(i)
            dict2 = {'Name' : x[0], 'Ensembl' : x[1] }
            dict1[str_i] = dict2
        return dict1
    except:

        return {'No Targets Found' : {'Name':'N/A', 'Ensembl': 'N/A'}}

# get_htf_target_data('AR')
