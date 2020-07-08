# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 12:16:34 2020

@author: Pratik Kayal
"""


import os
from flask import Flask


###########
##Config###
###########


class paramConfig():
    
    def __init__(self,subject):
        
        
        
        self.upload_folder = "Upload//"
        self.temp_folder = "Log//"
        self.predict_folder = "Scanned//"
        self.secret_key = '123SuccessIsNear456'
        
        
    
    
config = paramConfig(subject='Scanner Integration')