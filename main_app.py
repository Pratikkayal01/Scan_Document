# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 18:59:30 2020

@author: Pratik Kayal
"""


import os
#import urllib.request
from param_config import config
from flask import Flask, request, jsonify,send_file
from werkzeug.utils import secure_filename
from scanner import scanner_cl
#import pdb
import json
from threading import Thread


app = Flask(__name__)
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/<id>', methods=['POST'])
def upload_file(id):
    #pdb.set_trace()
    #token = request.args.get('token')
    trans_id = id
    if 1==1:
    #if token == config.secret_key:
        try:
            print(trans_id)
            print(type(trans_id))
            # check if the post request has the file part
            if 'file' not in request.files:
                resp = jsonify({'message' : 'No file part in the request'})
                resp.status_code = 400
                return resp
            file = request.files['file']
            if file.filename == '':
                resp = jsonify({'message' : 'No file selected for uploading'})
                resp.status_code = 400
                return resp
            if file and allowed_file(file.filename):
                print('In')
                #pdb.set_trace()
                filename = secure_filename(file.filename)
                file_extn = filename.split('.')[1]
                print(filename)
                filename = 'img_' + str(trans_id) + '_pdf.'+ str(file_extn)
                file.save(os.path.join(config.upload_folder, filename))
                print('message : File successfully uploaded')
                
                thread = Thread(target=scanner_cl.image_scanning, args=(filename,))
                thread.start()
                
                output = {'pollAfter':3000,'description':'File Recieved'}
                return jsonify(output)
                
            else:
                resp = jsonify({'message' : 'Allowed file types are png, jpg, jpeg'})
                resp.status_code = 400
                return resp
        except:
            resp = jsonify({'message' : 'Some error occured in the sytem'})
            resp.status_code = 400
            return resp
    else:
        return jsonify('Invalid Authentication')
    
    
@app.route('/status/<id>', methods=['GET'])
def status(id):
    
    trans_id = id
    
    error_fname = 'error_' + str(trans_id) + '.pdf'
    scanned_fname = str(trans_id) + '.pdf'
    
    error_path = config.temp_folder #+ error_fname
    scanned_path = config.predict_folder #+ scanned_fname
    
    flag = -99
    for root, dirs, files in os.walk(error_path):
        if error_fname in files:
            flag = -1
            json_2_sent = {'status':flag,'description':'Please Upload a better Image'}
    
    for root, dirs, files in os.walk(scanned_path):
        if scanned_fname in files:
            flag = 1
            json_2_sent = {'status':flag,'description':'Your Document is ready'}
   
    if flag not in [-1,1]:
        flag = 0
        json_2_sent = {'status':flag,'description':'We are working on your Image'}
    else:
        pass
    
    
    
    return jsonify(json_2_sent)

@app.route('/downloads/<id>', methods=['GET'])

def download(id):
    
    try:
        trans_id = id
        
        scanned_fname = str(trans_id) + '.pdf'
        scanned_path = config.predict_folder + scanned_fname 
        
        return send_file(scanned_path, as_attachment=True)
    
    except:
        return jsonify('Error')


if __name__ == "__main__":
    app.run()