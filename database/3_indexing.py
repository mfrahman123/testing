#to make the retrieval of data faster, we index the values we will look for in the tables. 

#open the database
db = SQL("sqlite:///chembl_28.db") 


#indexing
db.execute("CREATE INDEX Symbol_index ON HtfGandD (Symbol)")
db.execute("CREATE INDEX ensembl_index ON transcription_factors (Ensembl)")
db.execute("CREATE INDEX chromosome_index ON chromosomal_location (Chromosome)")
db.execute("CREATE INDEX Uniprot ON chromosomal_location (Uniprot_ID)")
db.execute("CREATE INDEX subcell_index ON protein_classification (definition)")
db.execute("CREATE INDEX function_index ON HtfLocation (Functions)")
db.execute("CREATE INDEX family_index ON transcription_factors (Family)")
db.execute("CREATE INDEX TID_index ON drug_mechanism (TID)") 
db.execute("CREATE INDEX chembl_index ON molecule_dictionary (CHEMBL_ID)")
db.execute("CREATE INDEX second_chembl_index ON HtfGandD (drug_concept_id)")
db.execute("CREATE INDEX second_symbol_index ON transcription_factors (Symbol)")
db.execute("CREATE INDEX third_symbol_index ON chromosomal_location (Symbol)")
db.execute("CREATE INDEX second_Uniprot_index ON HtfLocation (Uniprot)")
db.execute("CREATE INDEX first_molregno_index ON molecule_dictionary (MOLREGNO)")
db.execute("CREATE INDEX second_molregno_index ON molecule_synonyms (MOLREGNO)")
db.execute("CREATE INDEX third_molregno_index ON compound_structures (MOLREGNO)")
db.execute("CREATE INDEX fourth_molregno_index ON drug_mechanism (MOLREGNO)")
db.execute("CREATE INDEX fifth_molregno_index ON compound_records (MOLREGNO)")
db.execute("CREATE INDEX second_TID_index ON target_dictionary (TID)")
db.execute("CREATE INDEX gene_synonym_index ON component_synonyms(COMPONENT_SYNONYM) ")
db.execute("CREATE INDEX first_componentid_index ON component_synonyms (COMPONENT_ID)")
db.execute("CREATE INDEX second_componentid_index ON component_go (COMPONENT_ID)")
db.execute("CREATE INDEX third_componentid_index ON component_class (COMPONENT_ID)")
db.execute("CREATE INDEX first_protein_class_index ON component_class (PROTEIN_CLASS_ID)")
db.execute("CREATE INDEX second_protein_class_index ON protein_classification (PROTEIN_CLASS_ID)")
db.execute("CREATE INDEX third_protein_class_index ON protein_class_synonyms (PROTEIN_CLASS_ID)")
