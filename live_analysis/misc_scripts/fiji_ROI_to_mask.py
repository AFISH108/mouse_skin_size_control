#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 15:16:47 2022

@author: xies
"""

import numpy as np
import pandas as pd
from skimage import io, transform, draw
from os import path
from re import findall
import pickle as pkl
from glob import glob
from tqdm import tqdm

from twophoton_util import parse_unaligned_channels, parse_timecourse_directory

dirname = '/Users/xies/OneDrive - Stanford/Skin/06-25-2022/M1 WT/R1/'
dirname = '/Users/xies/OneDrive - Stanford/Skin/06-25-2022/M6 RBKO/R1/'

#%% Take all the annotated nuclei and draw them on unaligned images but with right aligned z-height

ALIGN = True

XX = 1024
ZZ = 95
T = 19

# reg_reg_list = parse_unaligned_channels(dirname)
# align_list = parse_timecourse_directory(dirname)

xfiles = sorted(glob(path.join(dirname,'manual_track/*/*/*.xpts.txt')))
yfiles = sorted(glob(path.join(dirname,'manual_track/*/*/*.ypts.txt')))
zfiles = sorted(glob(path.join(dirname,'manual_track/*/*/*.zpts.txt')))
coordinate_file_tuple = zip(xfiles,yfiles,zfiles)

if ALIGN:
    # Load transformation matrices
    _tmp = pkl.load(open(path.join(dirname,'alignment_information.pkl'),'rb'))
    dZ = np.array(_tmp[0]) - _tmp[2]

labeled_image = np.zeros((T,ZZ,XX,XX))

for fx,fy,fz in tqdm(coordinate_file_tuple):
    # parse timestamp
    t = int(findall('t(\d+)\.',path.basename(fx))[0])
    cellID = int(path.split(path.split(fx)[0])[1].split('.')[2])
        
    # Manually load list because line size is ragged
    with open(fx) as f:
        X = f.readlines()
    with open(fy) as f:
        Y = f.readlines()
    with open(fz) as f:
        Z = f.readlines()
        
    X = [np.array(line.strip('\n').split(','),dtype=int) for line in X]
    Y = [np.array(line.strip('\n').split(','),dtype=int) for line in Y]
    Z = np.array(Z[0].strip('\n').split(','),dtype=int)
    Z_ = Z - dZ[t]
    this_matrix = XY_matrices[t]
    
    for i, (x,y) in enumerate(zip(X,Y)):
        
        if Z_[i] < ZZ-1: #@todo: figure out why this is out of bounds sometimes
            RR,CC = draw.polygon(y,x)
            if ALIGN:
                tform = transform.EuclideanTransform(matrix = XY_matrices[t])
                coords = transform.matrix_transform(np.array((RR,CC)).T,tform.params).round().astype(int)
            else:
                coords = np.array((RR,CC)).T
            
            labeled_image[t,int(Z_[i]),coords[:,0],coords[:,1]] = cellID
        

io.imsave('/Users/xies/Desktop/blah.tif',labeled_image.astype(np.int16))


        
        
