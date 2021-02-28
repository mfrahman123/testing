#download the newest version of Chembl database from : https://chembl.gitbook.io/chembl-interface-documentation/downloads
#in this case the newest version is chembl_28. 

#Extract Chembl database
import tarfile

fname= 'chembl_28_sqlite.tar.gz'

if fname.endswith("tar.gz"):
    tar = tarfile.open(fname, "r:gz")
    tar.extractall()
    tar.close()
elif fname.endswith("tar"):
    tar = tarfile.open(fname, "r:")
    tar.extractall()
    tar.close()
