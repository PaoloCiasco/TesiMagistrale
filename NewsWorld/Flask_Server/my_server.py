import os
from flask import Flask, request, redirect, url_for, render_template
from prediction import Classifier
import prediction
import torch
import xml_csv_like
import xml_solr_like
import xml.etree.ElementTree as et
import pysolr
import requests


solr = pysolr.Solr('http://localhost:8983/solr/Iss_Report') # Istance of the Solr Index

# Parameters for the reload request of the core of the Solr Index


params = {
    'action': 'RELOAD',
    'core': 'Iss_Report',
}


UPLOAD_FOLDER = 'PATH_TO_THE_SERVER/Upload' 
ALLOWED_EXTENSIONS = {'xml'}

app = Flask(__name__, template_folder='Files')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.static_folder = 'static'

# Usage of the model found in the classification section

model = Classifier("Musixmatch/umberto-commoncrawl-cased-v1", num_labels=6, dropout_rate=0.2)
model.load_state_dict(torch.load("/home/paoloc/Flask_Server/state_dict_model_def.pth"))
model.eval()

@app.route("/")
def main():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/<name>')
def success(name):
    return render_template("upload_successful.html", content=name)
@app.route('/fail')
def fail():
    return render_template('upload_failed.html') 

@app.route('/query/<string>')
def search(string):
    results = solr.search(string, rows=16)
    return render_template('query.html', res = results)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(url_for('fail'))
        file = request.files['file']
        # If the user does not select a file or the extension is not correct,
        # redirect to the "fail" template.
        if file.filename == '':
            return redirect(url_for('fail'))
        if (allowed_file(file.filename) == False):
            return redirect(url_for('fail'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            patherino = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Gather the news from the file uploaded, make the prediction and
            # write the category in a .txt file. Read the category from the .txt 
            # and write it in the correct document in the xml file.
            index_path = xml_solr_like.index(patherino)
            tree = et.parse(index_path)
            myroot = tree.getroot()
            new_path = xml_csv_like.transform(patherino)
            f = open(new_path, "r", encoding="utf-8")
            phrases_to_be_predicted = f.readlines()
            preds = []
            i = 0
            file_path = "/home/paoloc/Flask_Server/Process/processtry.txt"
            if os.path.isfile(file_path):
                os.remove(file_path)
            for phrases in phrases_to_be_predicted:
                value = prediction.make_pred(phrases,model)
                preds.append(value)
                with open("/home/paoloc/Flask_Server/Process/processtry.txt", "a", encoding="utf-8") as f:
                    f.write(value + "\n")
            for child in myroot:        
                et.SubElement(child, "field", name="category").text = preds[i]
                i += 1
            et.indent(tree, space="\t", level=0)
            tree.write("/home/paoloc/Flask_Server/Indexing/File_to_be_indexed.xml")
            headers = {
                'Content-Type': 'text/xml',
            }

            with open('/home/paoloc/Flask_Server/Indexing/File_to_be_indexed.xml', 'rb') as f:
             data = f.read()

            response = requests.post('http://localhost:8983/solr/Iss_Report/update', headers=headers, data=data) # POST request for indexing
            response = requests.get('http://localhost:8983/solr/admin/cores', params=params)
            return redirect(url_for('success', name=filename))
    return '''
    <!doctype html>
    <title>NewsWorld</title>
    <h1>Process new .xml file</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    <p><a href="/"> Back to the Home! </p>
    '''

