#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 16:53:19 2022

@author: xies
"""


import numpy as np
import pandas as pd
from skimage import io, util
from os import path
from tqdm import tqdm


from twophotonUtils import parse_aligned_timecourse_directory


# dirname = '/Users/xies/OneDrive - Stanford/Skin/06-25-2022/M1 WT/R1'
# dirname = '/Users/xies/OneDrive - Stanford/Skin/Two photon/NMS/09-29-2022 RB-KO pair/RBKO/R2'
dirname = '/Users/xies/OneDrive - Stanford/Skin/Two photon/NMS/03-26-2023 RB-KO pair/M1 RBKO/R2'

filelist = parse_aligned_timecourse_directory(dirname)

#%% Stack channels & save into single tif

G = []
R = []
R_shg = []

for t in tqdm(range(len(filelist))):
    
    # G_ = io.imread(filelist.loc[t,'G'])
    # G.append(G_)
    R_ = io.imread(filelist.loc[t,'R'])
    R.append(R_)
    # R_shg_ = io.imread(filelist.loc[t,'R_shg'])
    # R_shg.append(R_shg_)
    
print('Saving ...')
# io.imsave(path.join(dirname,f'master_stack/G.tif'), np.stack(G).astype(np.uint16))
io.imsave(path.join(dirname,f'master_stack/R.tif'), np.stack(R).astype(np.uint16))
# io.imsave(path.join(dirname,f'master_stack/R_shg.tif'), np.stack(R_shg).astype(np.uint16))
   

#%% Save individual day*.tif into the same directory

MAX = 2**16-1
def fix_image_range(im, max_range):
    
    im = im.copy().astype(float)
    im[im == 0] = np.nan
    im = im - np.nanmin(im)
    im = im / np.nanmax(im) * max_range
    im[np.isnan(im)] = 0
    return im.astype(np.uint16)

for t in tqdm(range(T)):

# stack = np.zeros((Z_ref,3,XX,XX))
    
    R = io.imread(filelist.loc[t,'R'])
    G = io.imread(filelist.loc[t,'G'])
    B = io.imread(filelist.loc[t,'B'])
    
    # Do some image range clean up
    R_ = fix_image_range(R,MAX)
    G_ = fix_image_range(G,MAX)
    B_ = fix_image_range(B,MAX)

    stack = np.stack((R_,G_,B_))
    io.imsave(path.join(dirname,f'im_seq/t{t}.tif'),stack.astype(np.uint16),check_contrast=False)




