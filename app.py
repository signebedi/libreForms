from flask import Flask, flash, render_template, url_for, request, redirect, jsonify
import os, re, datetime, json
import plotly
import plotly.express as px
import pandas as pd
from libreforms import forms as form_src, db
from webargs import fields, flaskparser, ValidationError
from pymongo import MongoClient



def parse_form_fields(form=False):

    FORM_ARGS = {}           

    for field in form_src.forms[form].keys():

        if field.startswith("_"):
            pass
        elif form_src.forms[form][field]['output_data']['type'] == "str":
            FORM_ARGS[field] = fields.Str(
                        required=form_src.forms[form][field]['output_data']['required'],
                        validators=form_src.forms[form][field]['output_data']['validators'],)
        elif form_src.forms[form][field]['output_data']['type'] == "float":
            FORM_ARGS[field] = fields.Float(
                        required=form_src.forms[form][field]['output_data']['required'],
                        validators=form_src.forms[form][field]['output_data']['validators'],)
        elif form_src.forms[form][field]['output_data']['type'] == "list":
            FORM_ARGS[field] = fields.List(fields.String(),
                        required=form_src.forms[form][field]['output_data']['required'],
                        validators=form_src.forms[form][field]['output_data']['validators'],)
        elif form_src.forms[form][field]['output_data']['type'] == "int":
            FORM_ARGS[field] = fields.Int(
                        required=form_src.forms[form][field]['output_data']['required'],
                        validators=form_src.forms[form][field]['output_data']['validators'],)
        elif form_src.forms[form][field]['output_data']['type'] == "date":
            # FORM_ARGS[field] = fields.Date()
            FORM_ARGS[field] = fields.Str(
                        required=form_src.forms[form][field]['output_data']['required'],
                        validators=form_src.forms[form][field]['output_data']['validators'],)
        else:
            FORM_ARGS[field] = fields.Str(
                        required=form_src.forms[form][field]['output_data']['required'],
                        validators=form_src.forms[form][field]['output_data']['validators'],)

    return FORM_ARGS

# this function creates a list of the form fields 
# we want to pass to the web application
def progagate_forms(form=False):
        
    list_fields = form_src.forms[form]

    # here we drop the meta data fields    
    [list_fields.pop(field) for field in list(list_fields.keys()) if field.startswith("_")]
    
    return list_fields

# placeholder, will be used to parse options for a given form
def parse_options(form=False):
    
    # we start by reading the user defined forms into memory
    list_fields = form_src.forms[form]

    # we define the default values for application-defined options
    OPTIONS = {
        "_dashboard": False,
        "_allow_repeat": False, 
        "_allow_uploads": False, 
        "_allow_csv_templates": False,
        "_suppress_default_values": False,  
    }

    for field in list_fields.keys():
        if field.startswith("_"):
            # we overwrite existing option values, and add new ones
            # based on the user defined configurations
            OPTIONS[field] = list_fields[field]
    
    return OPTIONS


# create app object
app = Flask(__name__)
app.config["SECRET_KEY"] = "this is the secret key"


# read database password file, if it exists
if os.path.exists ("dbpw"):
    with open("dbpw", "r+") as f:
        dbpw = f.read().strip()
else:  
    dbpw=None

# initialize mongodb database
db = db.MongoDB(dbpw)

# define a home route
@app.route('/')
def home():
    homepage_msg = "Welcome to libreForms, an extensible form building abstraction \
                    layer implemented in Flask. Select a view from above to get started. \
                    Review the docs at https://github.com/signebedi/libreForms."

    return render_template('index.html', 
        homepage_msg=homepage_msg,
        type="home",
        name="libreForms",
    )


@app.route(f'/forms/')
def forms_home():
    return render_template('index.html', 
            homepage_msg="Select a table from the left-hand menu.",
            name="Form",
            type="forms",
            menu=[x for x in form_src.forms.keys()],
        ) 
        
@app.route(f'/tables/')
def table_home():
    return render_template('index.html', 
            homepage_msg="Select a table from the left-hand menu.",
            name="Table",
            type="table",
            menu=[x for x in form_src.forms.keys()],
        ) 

@app.route(f'/dashboards/')
def dashboard_home():
    return render_template('index.html', 
            homepage_msg="Select a dashboard from the left-hand menu.",
            name="Dashboard",
            type="dashboard",
            menu=[x for x in form_src.forms.keys()],
        ) 


# this creates the route to each of the forms
@app.route(f'/forms/<form_name>', methods=['GET', 'POST'])
def forms(form_name):

    try:
        forms = progagate_forms(form_name)

        if request.method == 'POST':
            parsed_args = flaskparser.parser.parse(parse_form_fields(form_name), request, location="form")
            db.write_document_to_collection(parsed_args, form_name)
            flash(str(parsed_args))

        return render_template('index.html', 
            context=forms,                                          # this passes the form fields as the primary 'context' variable
            name=form_name,                                         # this sets the name of the page for the page header
            menu=[x for x in form_src.forms.keys()],                # this returns the forms in libreform/forms to display in the lefthand menu
            type="forms",       
            options=parse_options(form=form_name),                      # here we pass the _options defined in libreforms/forms/__init__.py
            )

    except Exception as e:
        return render_template('index.html', 
            form_not_found=True,
            msg=e,
            name="404",
            type="forms",
            menu=[x for x in form_src.forms.keys()],
        )

# this creates the route to each of the tables
@app.route(f'/tables/<form_name>', methods=['GET', 'POST'])
def table(form_name): 

    try:
        pd.set_option('display.max_colwidth', 0)
        data = db.read_documents_from_collection(form_name)
        df = pd.DataFrame(list(data))
        df.drop(columns=["_id"], inplace=True)
        df.columns = [x.replace("_", " ") for x in df.columns]
    except Exception as e:
        df = pd.DataFrame(columns=["Error"], data=[{"Error":e}])

    return render_template('index.html',
        table=df,
        type="table",
        name=form_name,
        is_table=True,
        menu=[x for x in form_src.forms.keys()],
    )

# this creates the route to each of the dashboards
@app.route(f'/dashboards/<form_name>')
def dashboard(form_name):

    
    data = db.read_documents_from_collection(form_name)
    df = pd.DataFrame(list(data))
    ref = form_src.forms[form_name]["_dashboard"]['fields']

    # here we allow the user to specify the field they want to use, 
    # overriding the default y-axis field defined in libreforms/forms.
    # warning, this may be buggy
    if request.args.get("y"):
        y_context = request.args.get("y")

    else:
        y_context = ref['y']

    fig = px.line(df, 
                x=ref['x'], 
                y=y_context, 
                color=ref['color'])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', 
        graphJSON=graphJSON,
        name=form_name,
        type="dashboard",
        menu=[x for x in form_src.forms.keys()],
    )
        # return render_template('index.html', 
        #     form_not_found=True,
        #     msg="No dashboard has been configured for this form.",
        #     name="404",
        #     type="forms",
        #     menu=[x for x in form_src.forms.keys()],
        # )

        
if __name__ == "__main__":
    app.run(debug=True, host= '0.0.0.0', port='8000')
    
