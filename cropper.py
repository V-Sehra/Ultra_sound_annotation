#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 10:38:51 2022

@author: Vivek
"""
import cv2
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
cwd = os.getcwd()
back_s = [slash_idx for slash_idx in range(len(cwd))if cwd[slash_idx] =='/']
import imutils
import pickle
import imageio


def cropper (f_name,s_path,pat_id):
    def sizer(matrix_resize,image_resize, cord, string):
        #cord = [startY,endY,startX,endX]
        if string == '/body.png' or string == '/T_box.png' :
            matrix_resize[cord[0]-10:cord[1]+10,cord[2]-10:cord[3]+10] = 0
            image_resize[cord[0]-10:cord[1]+10,cord[2]-10:cord[3]+10] = 0
            
        if string == '/upper_box.png':
            matrix_resize[:cord[1]-5,:] = 0
            image_resize[:cord[1]-5,:] = 0
            
        if string == '/left_box.png':
            matrix_resize[:,:cord[3]+10] = 0
            image_resize[:,:cord[3]+10] = 0
            
        return(matrix_resize)
    
    def remover(matrix,image):    
        name_temp= ['/upper_box.png','/left_box.png','/body.png','/T_box.png']
        temp_path_vec = [cwd + '/crop_templets'+i for i in name_temp]
        # load the image image, convert it to grayscale, and detect edges
        for temp_id in range(len(temp_path_vec)):
            
            template = cv2.imread(temp_path_vec[temp_id])
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            template = cv2.Canny(template, 50, 200)
            (tH, tW) = template.shape[:2]
    
            
            found = None
            if name_temp[temp_id] == '/T_box.png':
                
                gray = cv2.cvtColor(image[0:int(image.shape[:2][0]*0.2),int(image.shape[:2][1]*0.5):], cv2.COLOR_BGR2GRAY)
            else:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            for scale in np.linspace(0.2, 1.0, 5)[::-1]:
            	# resize the image according to the scale, and keep track
            	# of the ratio of the resizing
            	resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
            	r = gray.shape[1] / float(resized.shape[1])
            	# if the resized image is smaller than the template, then break
            	# from the loop
            	if resized.shape[0] < tH or resized.shape[1] < tW:
            		break
                
            	edged = cv2.Canny(resized, 50, 200)
            	result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
            	(_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
                
                
                			# draw a bounding box around the detected region
            	clone = np.dstack([edged, edged, edged])
            	cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                				(maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
    
                		# if we have found a new maximum correlation value, then update
                		# the bookkeeping variable
            	if found is None or maxVal > found[0]:
            		found = (maxVal, maxLoc, r)
            	# unpack the bookkeeping variable and compute the (x, y) coordinates
            	# of the bounding box based on the resized ratio
            (_, maxLoc, r) = found
            (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
            (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
    
    
            if name_temp[temp_id] == '/T_box.png':
                startX = startX+int(image.shape[:2][1]*0.5)
                endX = endX+int(image.shape[:2][1]*0.5)
                
            matrix = sizer(matrix, image,[startY,endY,startX,endX], name_temp[temp_id])
            
        
        return(matrix)
    
    
    video_path = f_name
    cap = cv2.VideoCapture(video_path)
    frames=[]
    disp_frame = []
    
    while True:
        err,img = cap.read()
        if err:
            img = img[:,:885]
            frames.append(remover(np.array(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)),img))
            
            
        else:
            break

    
    video_name = f"{s_path}/{pat_id}_croppted.mp4"
    imageio.mimwrite(video_name, frames , fps = 30)
    
        
    frame_name = f"{s_path}/frames/{pat_id}_frames.pkl"
    with open(frame_name,'wb') as f:
        pickle.dump(frames,f)

    return(video_name)