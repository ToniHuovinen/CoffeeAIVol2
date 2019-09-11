# -*- coding: utf-8 -*-
"""
@author: Toni Huovinen
"""

from bs4 import BeautifulSoup  
from urllib.request import urlopen
import numpy as np
import cv2


url = "http://hindulaatti.ddns.net:3000/"
full_pot_area = 100000.0 # This value is taken from checking the contour area of a full pot image
empty_pot_area = 2000.0 # This value is taken from checking the contour area of almost empty pot image

def convert_image_return_threshold(img):
    # Convert the image to gray and then reduce sharpness with blurring
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    
    # Do binary thresholding to the blurred image, pixel color value 75 is cut off point, can be adjusted
    ret, thresh = cv2.threshold(blur, 83, 255, cv2.THRESH_BINARY_INV)
    return thresh


def find_contours(threshed_img):
    # Find the contours (edges) from the thresholded image
    contours = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
    return contours


def calculate_area(contours, max_value, min_value):
    # Find the largest contour (this is always the area of coffee pot) and calculate its area
    largest = max(contours, key = cv2.contourArea)
    area = cv2.contourArea(largest)
    print(area)
    # Normalize the area between 0 and 1 using the full and empty coffee pot values.
    # Multiply by 100 to get fill percentage
    converted_area = ((area - min_value) / (max_value - min_value) * 100)
    return converted_area


# For visualization
def visualize(contours, img_thresh, original_img):
    # Draw the contours in the original image, show original and thresholded side by side
    for c in contours:
        cv2.drawContours(original_img, [c], -1, (0,255,0), 2)
        
    cv2.imshow('threshold', img_thresh)
    cv2.imshow('original', original_img)



##################################################
# save all images from source (ict and seppis)

try:
    html = urlopen(url)
    soup = BeautifulSoup(html, features='lxml')
    
    for res in soup.findAll('img'):
        print(res.get('src'))
        list_var = url.split('/')
        resource = urlopen(list_var[0]+"//"+list_var[2]+res.get('src'))
        output = open(res.get('src').split('/')[-1],'wb')
        output.write(resource.read())
        output.close()

    # Read saved images. Files are stored in same location as python script
    # You can also read directly from source, no need to save files, adjust the code as needed
    img_ict = cv2.imread('ict_image.jpg')
    img_ict = img_ict[108:317, 346:554]
    
    img_seppis = cv2.imread('kahvi50.jpg') # Replace kahvi50 with seppis_image.jpg once camera is installed

    img_ict_thresh = convert_image_return_threshold(img_ict)
    img_seppis_thresh = convert_image_return_threshold(img_seppis)

    ict_contours = find_contours(img_ict_thresh)
    seppis_contours = find_contours(img_seppis_thresh)

    ict_pot_area = calculate_area(ict_contours, full_pot_area, empty_pot_area)
    seppis_pot_area = calculate_area(seppis_contours, full_pot_area, empty_pot_area)
    
    ict_value = ict_pot_area
    seppis_value = seppis_pot_area
    
    if ict_pot_area > 100:
        ict_pot_area = 100.0
        print("ICT office is full of coffee! Pls send help!")
    else:
        print("ICT Office Coffee Value is {}".format(round(ict_value, 2)))
        
    if seppis_pot_area > 100:
        seppis_pot_area = 100.0
        print("Seppis office is full of coffee! Pls send help!")
    


    # For visualizing whats happening
    visualize(ict_contours, img_ict_thresh, img_ict)

except:
    print("Something went wrong")

