from flask import Flask, render_template, url_for, redirect, request
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
import pandas as pd
import extract
import target
import gzip
from cs50 import SQL
import csv
from geo import open_gds

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename


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


@application.route('/')
def index():
    return render_template('index.html')

# define the action for the top level route
@application.route('/search', methods=['GET','POST'])
def search():
    form = QueryForm()
    htf_name = None

    if request.method == 'POST':
        htf_name = request.form.get('keywords')
        category_type = request.form.get('category')
        if category_type == 'tf':
            return redirect(url_for('tfprofile', htf_name = htf_name))
        elif category_type == 'gene':
            return 'gene'
        elif category_type == 'drug':
            return 'drug'
    return render_template('searchpage.html', form=form)

@application.route('/tfprofile/<htf_name>', methods=['GET'])
def tfprofile(htf_name):

    symbs = extract.get_symbols()

    if htf_name in symbs:
        db = SQL("sqlite:///chembl_28.db")

        user_inp = db.execute('''SELECT DISTINCT transcription_factors.Symbol, Ensembl, Chromosome, Family, Protein_name, Functions, Uniprot_ID, target_dictionary.PREF_NAME, protein_classification.SHORT_NAME, protein_classification.DEFINITION, SYNONYMS FROM HtfGandD
JOIN transcription_factors ON HtfGandD.Symbol = transcription_factors.Symbol
JOIN chromosomal_location ON transcription_factors.Symbol = chromosomal_location.Symbol
JOIN HtfLocation ON chromosomal_location.Uniprot_ID= HtfLocation.Uniprot
JOIN molecule_dictionary ON HtfGandD.drug_concept_id = molecule_dictionary.CHEMBL_ID
JOIN molecule_synonyms ON molecule_dictionary.MOLREGNO = molecule_synonyms.MOLREGNO
JOIN compound_structures ON molecule_synonyms.MOLREGNO = compound_structures.MOLREGNO
JOIN drug_mechanism ON compound_structures.MOLREGNO = drug_mechanism.MOLREGNO
JOIN target_dictionary ON drug_mechanism.TID = target_dictionary.TID
JOIN component_synonyms ON HtfGandD.Symbol = component_synonyms.COMPONENT_SYNONYM
JOIN component_go ON component_synonyms.COMPONENT_ID = component_go.COMPONENT_ID
JOIN component_class ON component_go.COMPONENT_ID = component_class.COMPONENT_ID
JOIN protein_classification ON component_class.PROTEIN_CLASS_ID = protein_classification.PROTEIN_CLASS_ID
JOIN protein_class_synonyms ON protein_classification.PROTEIN_CLASS_ID = protein_class_synonyms.PROTEIN_CLASS_ID
WHERE HtfGandD.Symbol =  ? ''', htf_name)
        
    
        list1_drugs =[]
        for n in range(len(user_inp)):
            test_synonyms = user_inp[n]['synonyms']  
            list1_drugs.append(test_synonyms)
        
        for num in range(len(user_inp)):
                       
            ensembl = user_inp[num]['Ensembl']
            chr = user_inp[num]['Chromosome']
            full_name = user_inp[num]['Protein_name'].title()
            uniprot = user_inp[num]['Uniprot_ID']
            subcell = user_inp[num]['definition']
            func = user_inp[num]['Functions']
            symbol = user_inp[num]['Symbol']
            family = user_inp[num]['Family']
            break
         
        targets = target.get_htf_target_data(htf_name)

        return render_template('tfprofile.html', symbol= symbol, ensembl=ensembl, family=family, chr=chr, full_name=full_name, uniprot=uniprot,
        subcell=subcell, func=func ,targets=targets, drug= list1_drugs)
        
    else:
        return redirect(url_for('error', htf_name = None))

@application.route('/error')
def error():
    return render_template('error.html')

@application.route('/download')
def download():
    return render_template('download.html')

@application.route('/geo',methods=['GET','POST'])
def geo():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        a = open_gds(f.filename)
        print(a)
    return render_template('GEO.html')

@application.route('/drugprofile')
def drugs():
    return render_template('drugprofile.html')

# @application.route('/browse/drugs/<htf_name>')
# def drugs():

#     return render_template('drugprofile.html')


# start the web server

# application.run(debug=True)
