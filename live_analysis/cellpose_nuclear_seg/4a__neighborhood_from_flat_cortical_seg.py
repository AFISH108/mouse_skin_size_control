#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 17:10:00 2022

@author: xies
"""


import numpy as np
from skimage import io, measure, util, morphology
from glob import glob
from os import path
from scipy import ndimage as ndi
from scipy.spatial import distance
import pandas as pd
import matplotlib.pylab as plt
from tqdm import tqdm


from imageUtils import draw_labels_on_image, draw_adjmat_on_image

dirname = '/Users/xies/OneDrive - Stanford/Skin/Mesa et al/W-R1/'
XX = 460
T = 15
corona = 2

def most_likely_label(labeled,im):
    label = 0
    if len(im[im>0]) > 0:
        unique,counts = np.unique(im[im > 0],return_counts=True)
        label = unique[counts.argmax()]
    return label

#%% Load the cytoplasmic segmentatinos

for t in range(6):

    # t = 4
    
    cyto_seg = io.imread(path.join(dirname,f'Image flattening/flat_cyto_seg_manual/t{t}.tif'))
    selem = ndi.generate_binary_structure(2,1)
    selem = ndi.iterate_structure(selem, corona)
    # allcytoIDs = np.unique(cyto_seg)[1:]
    
    dense_seg = io.imread(path.join(dirname,f'3d_nuc_seg/naive_tracking/t{t}.tif'))
    # heightmap = io.imread(path.join(dirname,f'Image flattening/heightmaps/t{t}.tif'))
    # heightmap = np.round(heightmap).astype(int)
    
    #% Label transfer from nuc3D -> cyto2D
    
    touching_threshold = 20 #px
    
    # For now detect the max overlap label with the nuc projection
    df_nuc = pd.DataFrame( measure.regionprops_table(dense_seg.max(axis=0), intensity_image = cyto_seg
                                                   ,properties=['label','centroid','max_intensity',
                                                                'euler_number','area']
                                                   ,extra_properties = [most_likely_label]))
    df_nuc = df_nuc.rename(columns={'centroid-0':'Y','centroid-1':'X'
                                      ,'most_likely_label':'CytoID','label':'CellposeID'})
    
    
    df_cyto = pd.DataFrame( measure.regionprops_table(cyto_seg, properties=['centroid','label']))
    df_cyto.index = df_cyto['label']
    
    nuc_coords = np.array([df_nuc['Y'],df_nuc['X']]).T
    cyto_coords = np.array([df_cyto['centroid-0'],df_cyto['centroid-1']]).T
    
    
    # Print non-injective mapping
    uniques,counts = np.unique(df_nuc['CytoID'],return_counts=True)
    bad_idx = np.where(counts > 1)[0]
    for i in bad_idx:
        print(f'CytoID being duplicated: {uniques[i]}')
    
    #% Relabel cyto seg with nuclear CellposeID
    
    df_cyto['CellposeID'] = np.nan
    for i,cyto in df_cyto.iterrows():
        cytoID = cyto['label']
        I = np.where(df_nuc['CytoID'] == cytoID)[0]
        if len(I) > 1:
            print(f'ERROR at {I}')
            break
        elif len(I) == 1:
            df_cyto.at[i,'CellposeID'] = df_nuc.loc[I,'CellposeID']
    
    
    #% Reconstruct adj network from cytolabels that touch
    
    A = np.zeros((len(df_nuc),len(df_nuc)))
    for i,cyto in tqdm(df_cyto.iterrows()):
        
        if np.isnan(cyto['CellposeID']):
            continue
        
        this_idx = np.where(df_nuc['CellposeID'] == cyto['CellposeID'])[0]
        
        this_mask = cyto_seg == cyto['label']
        this_mask_dil = morphology.binary_dilation(this_mask,selem)
        
        touchingIDs,counts = np.unique(cyto_seg[this_mask_dil],return_counts=True)
        touchingIDs[counts > touching_threshold] # should get rid of 'conrner touching'
        touchingIDs = touchingIDs[touchingIDs > 0] # Could touch background pxs
        touchingIDs = touchingIDs[touchingIDs != cyto['label']] # nonself
        
        # Convert CytoID to CellposeID
        touching_cellposeIDs = np.array([df_cyto.loc[tID]['CellposeID'] for tID in touchingIDs])
        touching_cellposeIDs = touching_cellposeIDs[~np.isnan(touching_cellposeIDs)].astype(int)
        
        # Convert CellposeID to idx in df_nuc
        touching_idx = np.where(np.in1d(df_nuc['CellposeID'], touching_cellposeIDs))[0]
        
        A[this_idx,touching_idx] = 1
    
    #% Save as matrix and image
    im_adj = draw_adjmat_on_image(A,nuc_coords,[XX,XX])
    io.imsave(path.join(dirname,f'Image flattening/flat_adj/t{t}.tif'),im_adj)
    
    # save matrix
    np.save(path.join(dirname,f'Image flattening/flat_adj/adjmat_t{t}.npy'),A)
    
    
    

