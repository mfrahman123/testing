from flask import Flask, render_template, url_for, redirect, request
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
import pandas as pd
import extract
import target
import gzip
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from cs50 import SQL
import csv
from geo import open_gds

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename


r = robjects.r

r['source']('R-visuals.R')
gseFUNC = robjects.globalenv['get_file_name']


# $env:FLASK_APP = "application.py"

extract.get_important_data()


# import sql ---> Uncomment if tranfac.db not present


# create a flask application object
# def create_app():
#     application = Flask(__name__)
#     Bootstrap(app)
#     FontAwesome(app)
#     application.config['SECRET_KEY'] = 'change this unsecure key'

#     return application
def create_app():
    application = Flask(__name__)
    Bootstrap(application)
    FontAwesome(application)
    application.config['SECRET_KEY'] = 'change this unsecure key'
    return application


application = create_app()


# we need to set a secret key attribute for secure forms

class QueryForm(FlaskForm):
    submit = SubmitField()


# define action for home page
@application.route('/')
def index():
    return render_template('index.html')


# define the action for search page
@application.route('/search', methods=['GET', 'POST'])
def search():
    form = QueryForm()
    htf_name = None

    if request.method == 'POST':
        htf_name = request.form.get('keywords')
        category_type = request.form.get('category')
        if category_type == 'tf':
            return redirect(url_for('tfprofile', htf_name=htf_name))
        elif category_type == 'gene':
            return redirect(url_for('tfprofile', htf_name=htf_name))
        elif category_type == 'drug':
            return 'drug'
    return render_template('searchpage.html', form=form)


# define actions for tf profiles
@application.route('/tfprofile/<htf_name>', methods=['GET', 'POST'])
def tfprofile(htf_name):
    symbs = extract.get_symbols()

    if htf_name in symbs:
        db = SQL("sqlite:///chembl_28.db")

        user_inp = db.execute('''SELECT DISTINCT transcription_factors.Symbol, Ensembl, Protein_name, Family, Chromosome, Uniprot_ID, Subcellular_location, Functions, drug_name, drug_concept_id FROM transcription_factors
LEFT JOIN chromosomal_location ON transcription_factors.Symbol = chromosomal_location.Symbol
LEFT JOIN HtfLocation ON chromosomal_location.Uniprot_ID = HtfLocation.Uniprot
LEFT JOIN HtfGandD ON chromosomal_location.Symbol= HtfGandD.Symbol
WHERE transcription_factors.Symbol = ?''', htf_name.upper())

        u_i = db.execute('''SELECT DISTINCT target_dictionary.PREF_NAME, protein_classification.SHORT_NAME, protein_classification.PARENT_ID, protein_classification.PROTEIN_CLASS_DESC, protein_classification.DEFINITION FROM transcription_factors
LEFT JOIN component_synonyms ON transcription_factors.Symbol = component_synonyms.COMPONENT_SYNONYM
LEFT JOIN component_class ON component_synonyms.COMPONENT_ID = component_class.COMPONENT_ID
LEFT JOIN protein_classification ON component_class.PROTEIN_CLASS_ID = protein_classification.PROTEIN_CLASS_ID
LEFT JOIN target_components ON component_synonyms.COMPONENT_ID = target_components.COMPONENT_ID
LEFT JOIN target_dictionary ON target_components.TID = target_dictionary.TID
WHERE transcription_factors.Symbol = ?''', htf_name.upper())

        try:

            dict1_drugs = {}
            for n in range(len(user_inp)):
                test_drug_name = user_inp[n]['drug_name']
                test_drug_concept_id = user_inp[n]['drug_concept_id']
                dict1_drugs[test_drug_concept_id] = test_drug_name
        except:

            dict1_drugs = {}
            test_drug_name = "None"
            test_drug_concept_id = "None"
            dict1_drugs[test_drug_concept_id] = test_drug_name

        for num in range(len(user_inp)):
            ensembl = user_inp[num]['Ensembl']
            chr = user_inp[num]['Chromosome']
            full_name = user_inp[num]['Protein_name'].title()
            uniprot = user_inp[num]['Uniprot_ID']
            subcell = user_inp[num]['Subcellular_location']
            func = user_inp[num]['Functions']
            symbol = user_inp[num]['Symbol']
            family = user_inp[num]['Family']
            break

        targets = target.get_htf_target_data(htf_name)

        return render_template('tfprofile.html', symbol=symbol, ensembl=ensembl, family=family, chr=chr,
                               full_name=full_name, uniprot=uniprot,
                               subcell=subcell, func=func, targets=targets, drug=dict1_drugs)

    else:
        return redirect(url_for('error', htf_name=None))


# define action for error page
@application.route('/error')
def error():
    return render_template('error.html')


# define action for download page
@application.route('/download')
def download():
    return render_template('download.html')


# define action for GEO upload page
@application.route('/geo',methods=['GET','POST'])
def geo():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        heatmap_create = gseFUNC(secure_filename(f.filename))
        return redirect(url_for('geo_results'))
    return render_template('GEO.html')

#
@application.route('/geo_results')
def geo_results():
    return render_template('GEO-results.html')


# define actions for drug profiles
@application.route('/drugprofile/<drug_name>', methods=['GET'])
def drug(drug_name):
    db = SQL("sqlite:///chembl_28.db")
    try:

        drug_data = db.execute('''SELECT DISTINCT molecule_dictionary.CHEMBL_ID, drug_name, action_type.ACTION_TYPE, target_dictionary.PREF_NAME, action_type.DESCRIPTION, HtfGandD.Symbol, MOLECULE_TYPE, FIRST_APPROVAL,  COMPOUND_NAME FROM HtfGandD  
    LEFT JOIN molecule_dictionary ON  HtfGandD.drug_concept_id = molecule_dictionary.CHEMBL_ID
    LEFT JOIN molecule_synonyms ON molecule_dictionary.MOLREGNO = molecule_synonyms.MOLREGNO
    LEFT JOIN compound_structures ON molecule_synonyms.MOLREGNO = compound_structures.MOLREGNO
    LEFT JOIN drug_mechanism ON compound_structures.MOLREGNO = drug_mechanism.MOLREGNO
    LEFT JOIN action_type ON drug_mechanism.ACTION_TYPE = action_type.ACTION_TYPE
    LEFT JOIN target_dictionary ON drug_mechanism.TID = target_dictionary.TID
    LEFT JOIN compound_records ON drug_mechanism.MOLREGNO = compound_records.MOLREGNO
    WHERE drug_name  = ?''', drug_name)


    except:
        drug_data = [{"pref_name": "None", "action_type": "None", "Symbol": "None", "compound_name": "None"}]

    for num in range(len(drug_data)):
        chembl_id = drug_data[num]['chembl_id']
        drug_name = drug_data[num]['drug_name']
        description = drug_data[num]['description']
        molecule_type = drug_data[num]['molecule_type']
        first_approval = drug_data[num]['first_approval']

        break

    return render_template('drugprofile.html', drug_data=drug_data, chembl_id=chembl_id, drug_name=drug_name,
                           description=description,
                           molecule_type=molecule_type, first_approval=first_approval)


# define actions for browse page
@application.route('/browse')
def tfbrowse():
    db = SQL("sqlite:///https://chembl-db.s3.eu-west-2.amazonaws.com/chembl_28.db")

    tfs = db.execute('''SELECT DISTINCT transcription_factors.Symbol, Protein_name FROM transcription_factors
                        JOIN chromosomal_location ON transcription_factors.Symbol = chromosomal_location.Symbol''')

    try:

        dict1_tfs = {}
        for i in tfs:
            full_name = i['Protein_name']
            symbol = i['Symbol']
            dict1_tfs[symbol] = full_name
    except:

        dict1_tfs = {}
        full_name = "None"
        symbol = "None"
        dict1_tfs[symbol] = full_name

    return render_template('browse.html', tf=dict1_tfs)

# start the web server

#application.run(debug=True)

