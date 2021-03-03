#Import relevant packages
from flask import Flask, render_template, url_for, redirect, request
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
import extract
import target
import rpy2.robjects as robjects
from cs50 import SQL

from flask_wtf import FlaskForm
from wtforms import SubmitField
from werkzeug.utils import secure_filename

import RA
import radt

#extract all functions from R code
r = robjects.r
r['source']('R-visuals.R')
gseFUNC = robjects.globalenv['get_file_name']
#heatFUNC = robjects.globalenv['get_file_name2']
raFUNC = robjects.globalenv['relative_activity']
clearFUNC = robjects.globalenv['clear_env']
# $env:FLASK_APP = "application.py"
extract.get_important_data()


# import sql ---> Uncomment if tranfac.db not present

# create Flask application to allow for specific routes to be created. 
def create_app():
    application = Flask(__name__)
    Bootstrap(application)
    FontAwesome(application)
    application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

    return application

application = create_app()

#create Form class for user input in search page
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
    #once user submits input then send them to POST method. 
    #Take account for lower case input
    if request.method == 'POST':
        #identify what category the user selected
        category_type = request.form.get('category')
        #if user selects transcription factor/gene category request their input and send them to tfprofile page
        if category_type == 'tf':
            htf_name = request.form.get('keywords')
            return redirect(url_for('tfprofile', htf_name=htf_name.upper()))
        #if user selects drug category request their input and send them to drug page
        elif category_type == 'drug':
            drug_name = request.form.get('keywords')
            return redirect(url_for('drug', drug_name=drug_name.upper()))
    return render_template('searchpage.html', form=form)


# define actions for tf profiles
@application.route('/tfprofile/<htf_name>', methods=['GET', 'POST'])
def tfprofile(htf_name):
    
    #get all existing human tf symbol data
    symbs = extract.get_symbols()
    
    #if user enters tf that is present from existing human tf symbol data extract relevant data and return html template for tfprofile with relevant data.
    if htf_name in symbs:
        db = SQL("sqlite:///transfacts.db")

        htf_name = htf_name.upper()

        user_inp = db.execute('''SELECT * FROM Htf_info WHERE Symbol = ?''', htf_name)

        u_i = db.execute('''SELECT * FROM Protein_info WHERE Symbol = ?''', htf_name)
        #if data exists for drugs in transfacts.db then extract and return relevant information
        try:

            dict1_drugs = {}
            for n in range(len(user_inp)):
                test_drug_name = user_inp[n]['drug_name']
                test_drug_concept_id = user_inp[n]['drug_concept_id']
                dict1_drugs[test_drug_concept_id] = test_drug_name
        #if data doesn't exist for drugs in transfacts.db then extract and return 'None' for each data cell.
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
        #get drug target information from hTF Target DB
        targets = target.get_htf_target_data(htf_name)

        return render_template('tfprofile.html', symbol=symbol, ensembl=ensembl, family=family, chr=chr,
                               full_name=full_name, uniprot=uniprot,
                               subcell=subcell, func=func, targets=targets, drug=dict1_drugs)
    #send to error page if user inputs symbol which is not a human tf
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


# define actions for GEO pages
@application.route('/geo',methods=['GET','POST'])
def geo():
    #clear R environment
    clearFUNC()
    #send site to POST method
    if request.method == 'POST':
        #get file name
        f = request.files['file']
        f.save(secure_filename(f.filename))
        #create heatmap(s)
        heatmap_create = gseFUNC(secure_filename(f.filename))
        #heatmap2_create = heatFUNC(secure_filename(f.filename))
        #create gene expression data matrix and human transcription factor matrix for plsgenomic package in R
        a = RA.ge_data(secure_filename(f.filename))
        a.to_csv("ge_data.csv")
        b = RA.connec_data(a)
        b.to_csv('connec_data.csv')
        raFUNC()

        #send user to geo data visualisations or relative activity results page
        return redirect(url_for('geo_results'))
    return render_template('GEO.html')

#define actions for GEO relative activity results page
@application.route('/geo_results')
def geo_results():
    #extract column names and row items from relative activity csv file created by R
    colnames = radt.column_names()
    rownames = radt.row_names()
    return render_template('GEO-results.html',  colnames=colnames, rownames=rownames)


#define actions for GEO data visualisations page
@application.route('/geo_vis')
def geo_vis():

    return render_template('GEO-vis.html')



# define actions for drug profiles
@application.route('/drugprofile/<drug_name>', methods=['GET', 'POST'])
def drug(drug_name):
    #get data from transfacts.db
    db = SQL("sqlite:///transfacts.db")
    
    #extract relevant information if found or catch error and return suitable information
    try:

        drug_data = db.execute('''SELECT * FROM drug_info WHERE drug_name  = ?''', drug_name)


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
    #get data from transfacts.db

    db = SQL("sqlite:///transfacts.db")

    tfs = db.execute('''SELECT * FROM browse_info''')
    
    #get protein name and gene symbol data from db and catch error
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

# No caching at all for API endpoints.
@application.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response
# start the web server

#application.run(debug=True)
