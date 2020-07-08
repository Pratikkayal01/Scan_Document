# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 11:48:15 2020

@author: Pratik Kayal
"""


from __future__ import division
import numpy as np
import cv2
import imutils
import img2pdf 
from PIL import Image 
import os
#from skimage.filters import threshold_local
from param_config import config
import shutil
#import pdb


class scanner():
    
    def __init__(self):
        value_p = True
        
        
    def order_points(self,pts):
        rect = np.zeros((4, 2), dtype = "float32")
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect
    
    def four_point_transform(self,image, pts):
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype = "float32")
        
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        return warped
    
    def image_2_PDF(self,img,pdf):
        
        image = Image.open(img)
    
        # storing pdf path 
        pdf_path = pdf
        # converting into chunks using img2pdf 
        pdf_bytes = img2pdf.convert(image.filename) 
    
        # opening or creating pdf file 
        file = open(pdf_path, "wb") 
        # writing pdf files with chunks 
        file.write(pdf_bytes) 
        # closing image file 
        image.close() 
        # closing pdf file 
        file.close() 
    
        # output 
        print("Successfully made pdf file")
        
        
    def find(self,name):
        path = config.upload_folder
        for root, dirs, files in os.walk(path):
            if name in files:
                return 1
            else:
                return 0
        
    def image_scanning(self,filename):
        
        file_exists = self.find(filename)
        
        if file_exists == 1:
            
            
            try:
                
                img_path = config.upload_folder + filename
    
                image = cv2.imread(img_path)
                ratio = image.shape[0] / 500.0
                orig = image.copy()
                image = imutils.resize(image, height = 500)
                # convert the image to grayscale, blur it, and find edges
                # in the image
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (5, 5), 0)
                edged = cv2.Canny(gray, 75, 200)
                

                cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
                
                cnts = sorted(cnts, key = cv2.contourArea, reverse = True)
                
                # loop over the contours
                for c in cnts:
                    # approximate the contour
                    peri = cv2.arcLength(c, True)
                    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                    # if our approximated contour has four points, then we
                    # can assume that we have found our screen
        
                    if len(approx) == 4:
                        screenCnt = approx
                        break
                cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
                
                screenCnt = screenCnt.reshape(4, 2) * ratio
                
                
                warped = self.four_point_transform(orig, screenCnt)
                warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
                #T = threshold_local(warped, 20, offset = 5, method = "gaussian")
                #warped = (warped > T).astype("uint8") * 255
                
                temp_img_path = config.temp_folder + 'tmp_' + filename
                cv2.imwrite(temp_img_path, warped)
                
                
                
                scanned_filename = filename.split('_')[1]
                scannedPath = config.predict_folder + str(scanned_filename) + '.pdf'
                
                
                self.image_2_PDF(temp_img_path,scannedPath)
            
            except:
                
                base_dir =  'error.pdf'
                
                err_fileName = filename.split('_')[1]
                dest_folder = config.temp_folder + 'error_' + str(err_fileName)+'.pdf'
                
                shutil.copy(base_dir,dest_folder)
        else:
            base_dir = config.base_dir + 'error.pdf'
                
            err_fileName = filename.split('_')[1]
            dest_folder = config.temp_folder + 'error_' + str(err_fileName)+'.pdf'
                
            shutil.move(base_dir,dest_folder)
            
scanner_cl = scanner()
