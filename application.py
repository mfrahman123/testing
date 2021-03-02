#Add Imports
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

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename

import RA
import radt

#set up R code through rpy2 
r = robjects.r
r['source']('R-visuals.R')
gseFUNC = robjects.globalenv['get_file_name']
raFUNC = robjects.globalenv['relative_activity']
clearFUNC = robjects.globalenv['clear_env']
filepath = ''
# $env:FLASK_APP = "application.py"

extract.get_important_data()


# import sql ---> Uncomment if tranfac.db not present


# create a flask application object with Boostrap and FontAwesome capabilities
def create_app():
    application = Flask(__name__)
    Bootstrap(application)
    FontAwesome(application)
    application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

    return application


application = create_app()


#Set up flask form for user input
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
    #configure searchbar for when user inputs category of either drug or gene name
    if request.method == 'POST':
        category_type = request.form.get('category')
        if category_type == 'tf':
            htf_name = request.form.get('keywords')
            return redirect(url_for('tfprofile', htf_name=htf_name.upper()))
        elif category_type == 'drug':
            drug_name = request.form.get('keywords')
            return redirect(url_for('drug', drug_name=drug_name.upper()))
    return render_template('searchpage.html', form=form)


# define actions for tf profiles
@application.route('/tfprofile/<htf_name>', methods=['GET', 'POST'])
def tfprofile(htf_name):
    #extract all symbols
    symbs = extract.get_symbols()
    #identify if the gene symbol entered is present within a list of all the current human transcription factor genes
    if htf_name in symbs:
        #extract relevant tf information from sql database
        db = SQL("sqlite:///transfacts.db")

        htf_name = htf_name.upper()

        user_inp = db.execute('''SELECT * FROM Htf_info WHERE Symbol = ?''', htf_name)

        u_i = db.execute('''SELECT * FROM Protein_info WHERE Symbol = ?''', htf_name)
        #Take account for if there is no data present for the input that is entered and provide exception
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
        
        #extract key transcription factor background information
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
        #Extract target gene information that they are known to regulate
        targets = target.get_htf_target_data(htf_name)

        return render_template('tfprofile.html', symbol=symbol, ensembl=ensembl, family=family, chr=chr,
                               full_name=full_name, uniprot=uniprot,
                               subcell=subcell, func=func, targets=targets, drug=dict1_drugs)
    #send to error page if no key data found
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
    #clear R environment
    clearFUNC()
    #once user uploads file send to POST method
    if request.method == 'POST':
        #get file name and save in directory 
        f = request.files['file']
        f.save(secure_filename(f.filename))
        #create heatmap image
        heatmap_create = gseFUNC(secure_filename(f.filename))

        #provide gene expression data and human transcription factor CHIP-SEQ matrix data for plsgenomics package in R to estimate transcription factor activity values
        ge = RA.ge_data(secure_filename(f.filename))
        ge.to_csv("ge_data.csv")
        connec = RA.connec_data(a)
        connec.to_csv('connec_data.csv')
        #create relative activity table and export as csv to main directory
        raFUNC()

        #send user to results page
        return redirect(url_for('geo_results'))
    return render_template('GEO.html')

#define action for geo data visualitions
@application.route('/geo_results')
def geo_results():
    #extract column and row data from relative activity csv file in order to export to html for table format
    colnames = radt.column_names()
    rownames = radt.row_names()
    return render_template('GEO-results.html',  colnames=colnames, rownames=rownames)

# @application.route('/geo_vis')
# def geo_vis():
#
#     return render_template('GEO-vis.html')



# define actions for drug profiles
@application.route('/drugprofile/<drug_name>', methods=['GET', 'POST'])
def drug(drug_name):
    #extract relevant drug information from sql database
    db = SQL("sqlite:///transfacts.db")
    try:
        
        drug_data = db.execute('''SELECT * FROM drug_info WHERE drug_name  = ?''', drug_name)

    #Take account for drug data if not found
    except:
        drug_data = [{"drug_name": "None", "ACTION_TYPE": "None", "Symbol": "None", "COMPOUND_NAME": "None"}]
    
    for num in range(len(drug_data)):
        chembl_id = drug_data[num]['CHEMBL_ID']
        drug_name = drug_data[num]['drug_name']
        description = drug_data[num]['DESCRIPTIONS']
        molecule_type = drug_data[num]['MOLECULE_TYPE']
        first_approval = drug_data[num]['FIRST_APPROVAL']

        break
    
    return render_template('drugprofile.html', drug_data=drug_data, chembl_id=chembl_id, drug_name=drug_name,
                           description=description,
                           molecule_type=molecule_type, first_approval=first_approval)


# define actions for browse page
@application.route('/browse')
def tfbrowse():
    #extract all transcription factor gene symbols and protein names 
    db = SQL("sqlite:///transfacts.db")

    tfs = db.execute('''SELECT * FROM browse_info''')

    try:

        dict1_tfs = {}
        for i in tfs:
            full_name = i['Protein_name']
            symbol = i['Symbol']
            dict1_tfs[symbol] = full_name
    except:
    #account for no data being found in sql database
        dict1_tfs = {}
        full_name = "None"
        symbol = "None"
        dict1_tfs[symbol] = full_name

    return render_template('browse.html', tf=dict1_tfs)

# No caching at all for API endpoints.
@application.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response
# start the web server

application.run(debug=True)

