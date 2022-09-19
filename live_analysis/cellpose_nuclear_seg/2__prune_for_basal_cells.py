#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 12:29:50 2022

@author: xies
"""

import numpy as np
from skimage import io, measure
from glob import glob
from os import path
import pandas as pd
import matplotlib.pylab as plt
from matplotlib.path import Path
from SelectFromCollection import SelectFromCollection

'''

1. Load cellpose output on whole z stack
2. Use heightmap and identify the likely 'basal z-range' and get rid of things more apical
3. get rid of small + large objects

'''

dirname = '/Users/xies/OneDrive - Stanford/Skin/Mesa et al/W-R1/'
# filenames = glob(path.join(dirname,'Cropped_images/20161127_Fucci_1F_0-168hr_W_R1_cropped.tif'))
dirname = '/Users/xies/OneDrive - Stanford/Skin/Confocal/08-26-2022/10month 2week induce/Paw H2B-CFP FUCCI2 Phall647/RBKO1'
filenames = glob(path.join(dirname,'RBKO1.tif'))

#%%

# pred_files = glob(path.join(dirname,'h2b_sequence/*/t*_masks.tif'))
T = 1

# Some pruning parameters
# MIN_SIZE_IN_PX = 2000

_tmp = []
for t in range(T):
    
    # predictions = io.imread(path.join(dirname,f'im_seq/t{t}_3d_cyto/t{t}_masks.tif'))
    predictions = io.imread(path.join(dirname,f'RBKO1_nuc_masks.tif'))
    heightmaps = io.imread(path.join(dirname,f'Image flattening/heightmaps/RBKO1.tif'))
    table = pd.DataFrame(measure.regionprops_table(predictions,properties={'label','area','centroid'}))
    
    # Look at each XY coord and look up heightmap
    Z = heightmaps[ table['centroid-1'].round().astype(int), table['centroid-1'].round().astype(int) ]
    table['Corrected Z'] = table['centroid-0'] - Z
    
    table['Time'] = t
    _tmp.append(table)
    

#%%%

# ts = ax.scatter(grid_x, grid_y)

df = pd.concat(_tmp)

plt.scatter(df['area'],df['Corrected Z'],alpha=0.01)
plt.ylabel('Corrected Z (to heightmap)')
plt.xlabel('Cell size (px2)')
# plt.xlim([0,25000])
# gate = roipoly()

selector = SelectFromCollection(plt.gca(), pts)

#%%

verts = np.array(selector.poly.verts)
x = verts[:,0]
y = verts[:,1]

p_ = Path(np.array([x,y]).T)
I = np.array([p_.contains_point([x,y]) for x,y in zip(df['area'],df['Corrected Z'])])
# I = p_.contains_points( np.array([df['area'],df['Corrected Z']]).T )

# df_ = df[I]
# plt.scatter(df['area'],df['centroid-0'],alpha=0.5)
# plt.scatter(df_['area'],df_['centroid-0'],color='r')

#%% # Reconstruct the filtered segmentation predictions

for t in range(T):
    
    # predictions = io.imread(path.join(dirname,f'im_seq/t{t}_3d_cyto/t{t}_masks.tif'))
    predictions = io.imread(path.join(dirname,f'RBKO1_nuc_masks.tif'))
    this_cellIDs = df_[df_['Time'] == t]['label']
    
    filtered_pred = predictions.flatten()
    I = np.in1d(predictions.flatten(), this_cellIDs)
    filtered_pred[~I] = 0
    filtered_pred = filtered_pred.reshape(predictions.shape)
    
    # io.imsave(path.join(dirname,f'3d_cyto_seg/cellpose_cleaned/t{t}.tif'),filtered_pred.astype(np.int16))
    io.imsave(path.join(dirname,f'RBKO1_nuc_seg_cleaned.tif'),filtered_pred.astype(np.int16))
    


