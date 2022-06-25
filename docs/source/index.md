![header img](header_img_large.png)

## about
Liberate your forms with libreForms, an open form manager API that's intended to run in your organization's intranet. Most browser-based form managers lack key features, direct control over the underlying application, self-hosting support, a viable cost/licensing model, or lightweight footprints. The libreForms project, first and foremost, defines a simple but highly extensible abstraction layer that matches form fields to data structures. It adds a browser-based application, document-oriented database, and data visualizations and a RESTful API on top of this. 

![abstraction layer](libreForms_abstraction_layer.drawio.svg)

## use cases
- You are a small enterprise that has been using Google Forms for your organization's internal forms because it is low-cost, but you dislike the restricted features and lack of direct control over your data.

- You are a medium-sized enterprise that wants a simple, low-cost tool to manage their internal forms. You don't mind self-hosting the application, and you have staff with rudimentary experience using Python to deploy and maintain the system.

- You are a large enterprise with significant technical staff that routinely host and maintain applications for use on your organization's intranet. You have assessed options for form managers on the market and determined that proprietary services provide little direct control over the application source code, or otherwise fail to provide a viable licensing model.

## features
- a form-building abstraction layer based on Python dictionaries
- a flask web application (http://x.x.x.x:8000/) that will work well behind most standard reverse-proxies 
- plotly dashboards for data visualization
- a document-oriented database to store form data 
- \[future\] local and SAML authentication options
- \[future\] support for lookups in form fields & routing lists for form review, approvals, and notifications



## Installation (RHEL 8)

0. install dependencies

```
# see https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-red-hat/
echo "[mongodb-org-5.0] 
name=MongoDB Repository 
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/5.0/x86_64/ 
gpgcheck=1 
enabled=1 
gpgkey=https://www.mongodb.org/static/pgp/server-5.0.asc" | tee /etc/yum.repos.d/mongodb-org-5.0.repo
yum update -y
yum install python3.8 mongodb-org -y
systemctl enable --now mongodb
```

1. Download this repository into the opt directory:

**Method 1: `wget` stable release**

```
cd /opt
wget https://github.com/signebedi/libreForms/archive/refs/tags/X.X.X.tar.gz
tar -xvf libreforms-*.*.*.tar.gz
mv libreforms-*.*.* libreForms
```

**Method 2: `git clone` cutting edge repository**

```
cd /opt
git clone https://github.com/signebedi/libreForms.git
```

2. install Python virtual environment and initialize flask

```
cd /opt/libreForms
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app
flask init-db
```

3. libreforms user

```
useradd --no-create-home --system libreforms
chown -R libreforms:libreforms /opt/libreForms
```

4. systemd service

```
cp /opt/libreForms/gunicorn/libreforms.service /etc/systemd/system
systemctl daemon-reload
systemctl enable --now libreforms
```

## Installation (Ubuntu 20.04)

0. install dependencies

```
apt update -y && apt upgrade -y
apt install -y mongodb python3-pip python3-venv # for the most up to date version of mongodb, see https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/
systemctl enable --now mongodb
```

1. Download this repository into the opt directory:

**Method 1: `wget` stable release**

```
cd /opt
wget https://github.com/signebedi/libreForms/archive/refs/tags/X.X.X.tar.gz
tar -xvf libreforms-*.*.*.tar.gz
mv libreforms-*.*.* libreForms
```

**Method 2: `git clone` cutting edge repository**

```
cd /opt
git clone https://github.com/signebedi/libreForms.git
```

2. install Python virtual environment and initialize flask

```
cd /opt/libreForms
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app
flask init-db
```

3. libreforms user

```
useradd --no-create-home --system libreforms
chown -R libreforms:libreforms /opt/libreForms
```

4. systemd service

```
cp /opt/libreForms/gunicorn/libreforms.service /etc/systemd/system
systemctl daemon-reload
systemctl enable --now libreforms
```

if you experience a failure when you check `systemctl status libreforms`, then try chowning the program files and restarting the application.

```
chown -R libreforms:libreforms /opt/libreForms
systemctl restart libreforms
```


## API

The purpose of the libreForms project is to provide a simple but highly extensible method of form building in Python, leveraging Flask's doctrine of 'simplicity and extensibility' to give significant control and flexibility to organizations to design forms and data that meet their needs. 

The application provides an API for storing all the information it needs to generate a browser-based form within a Python dictionary. Given the project's emphasis on supporting arbitrary data structures, it translates these form fields into data structures intended to be stored in a JSON-like Document database like MongoDB, which it supports out-of-the-box, and creates a separate collection for each unique form with the presumption that the documents contained therein will adhere to a data structure that contains some set of common fields upon which data may be collated.

libreForms defines a robust abstraction layer (the config file for which is located at ```libreforms/forms/__init__.py```, which can be overwritten and/or extended by adding a file called ```libreforms/forms/add_ons.py```) between (1) the types of form fields that are used to collect user data and (2) the data type that the content of these form fields take, once submitted by the user, and (3) the underlying data structure of form responses, which the system stores in a JSON-like database well suited to integration with useful data science tools like pandas, as well as visualization libraries like plotly. Specifically, this API supports the following types of HTML form fields:

- "text"
- "password"
- "radio"
- "checkbox"
- "date"
- "hidden"
- "number"
- "file"

as well as the following output data types:

- str
- float
- int
- list

The “input_field” key refers only to the structure of the markup field that will be used to collect the data; all the information regarding the typing and validation of the data exists in the “output_data” key. for each form, optional, non-form-field data is defined with an underscore (_) preceding the key name, like _allow_repeats. All of these are optional fields and default to a value of False.

Here is an example form “sample-form” with all the allowed form fields given as examples:

```python
# libreforms/forms/__init__.py: the source for form field data in the libreForms application.
import datetime
 
forms = {
"sample-form": {
    "Text_Field": {
        "input_field": {"type": "text", "content": ["NA"]},
        "output_data": {"type": "str", "validators": [lambda p: len(p) >= 6]},
       },
    "Pass_Field": {
        "input_field": {"type": "password", "content": [""]},
        "output_data": {"type": "str", "validators": []},
       },
    "Radio_Field": {
        "input_field": {"type": "radio", "content": ["Pick", "An", "Option"]},
        "output_data": {"type": "str", "validators": []},
       },
    "Check_Field": {
        "input_field": {"type": "checkbox", "content": ["Pick", "An", "Option"]},
        "output_data": {"type": "list", "validators": []},
       },
    "Date_Field": {
        "input_field": {"type": "date", "content": [datetime.datetime.today().strftime("%Y-%m-%d")]},
           # "input_field": {"type": "date", "content": []},
        "output_data": {"type": "date", "validators": []},
       },
    "Hidden_Field": {
        "input_field": {"type": "hidden", "content": ["This field is hidden"]},
        "output_data": {"type": "str", "validators": []},
       },
    "Float_Field": {
        "input_field": {"type": "number", "content": [0]},
        "output_data": {"type": "float", "validators": []},
       },
    "Int_Field": {
        "input_field": {"type": "number", "content": [0]},
        "output_data": {"type": "int", "validators": []},
       },
#      "File_Field": {
#          "input_field": {"type": "file", "content": [None]}, # still need to review https://flask.palletsprojects.com/en/2.1.x/patterns/fileuploads/
#          "output_data": {"type": TBD, "validators": []},
#         },
    "_dashboard": {             # defaults to False
        "type": "scatter",      # this is a highly powerful feature but requires
        "fields": {             # some knowledge of plotly dashboards; currently
            "x": "Timestamp",   # only line charts with limited features supported
            "y": "Num_Field",
            "color": "Text_Field"
           }
       },
    "_allow_repeat": False, # defaults to False
    "_allow_uploads": False, # defaults to False
    "_allow_csv_templates": False, # defaults to False
   },
}
```

The application presumes that authentication is set in place & adds the following to each database write:

    - _id: unique id for each db write
    - Reporter: the username of the reporting user
    - Timestamp: the timestamp that the form was submitted


## REST API

There is a RESTful API that allows users to complete read and, in the future, write operations against the MongoDB database. This requires API keys. You can create a file in the application home directory called `api_keys` structured as:

```
api_keys
t32HDBcKAAIVBBPbjBADCbCh
```

But if you don't, the default test key will be `t32HDBcKAAIVBBPbjBADCbCh`. 

## extensibility

If you'd like to extend the content of ```libreforms/forms/__init__.py```, you can do so by adding a file called ```libreforms/forms/add_ons.py```. This file should replicate the structure of `__init__.py` by defining a dictionary called ```forms``` conforming to the above API. The default behavior is for this dictionary to overwrite the ```forms``` dictionary defined in `__init__.py`. However, if for some reason it is preferrable to append the dictionary, this is stored in a dictionary called forms_appended (which can be called by importing from libreforms.forms.forms_appended instead of libreforms.forms.forms).

## selectors

libreForms allows users to tailor the data in their dashboards and tables using GET variabes as selectors. For example, when you define a dashboard for a given form, you need to set a dependent variable. However, this can be overridden by passing the ```?y=field_name``` GET variable in the browser. Likewise, you can tailor tabular data by passing the ```?FIELD_NAME=VALUE``` GET variable in the browser. Put another way, if a table has a field called ```Sub-Unit``` and another called Fiscal_Year, and you would like to tailor the table to only show data for the Finance sub-unit in the 2021 fiscal year, then you could pass the following GET variables: ```?Sub-Unit=Finance&Fiscal_Year=2021``` to select only this data.

## database

If you elect to password protect your database, which is recommended, you should drop a file in the application home directory named ```mongodb_pw``` and ensure that the ```libreforms``` user has read access.

## dashboards

Right now, only line graphs are supported. In the future, the project plans to allow arbitrary dashboard configurations.

## display overrides

You can override some of the default site display options by adding a file called `site_overrides.py` to the project home directory. This file should contain a dictionary object with key-value attributes that you want to override. 

```
display = {
    'site_name':"My-Site",
    'homepage_msg': "Welcome to My-Site. Select a view from above to get started.",
    'warning_banner':"Please be mindful of the data you post on this system.",
    'favicon':"my_new_favicon.ico",
    'default_org':"My Organization's Name",
}
```

## auth

By default, this application employs an sqlite user database. The default login credentials are 

```
User: libreforms
Pass: libreforms
```

In addition to username and password fields, the application ships by default with phone number, organization, and email fields. These can be modified by changing the fields defined in app/schema.sql and app/auth.py. Currently, there is no group-based permission sets defined, but these will be added per https://github.com/signebedi/libreForms/issues/16.


## copyright

```
libreForms is an open form manager API
Copyright (C) 2022 Sig Janoska-Bedi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```





```{toctree}
---
maxdepth: 2
numbered: 0
---
```