#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 19:20:32 2022

@author: xies
"""

from skimage import io,measure

dirname = '/Users/xies/OneDrive - Stanford/Skin/Mesa et al/W-R1/'

def most_likely_label(labeled,im):
    label = 0
    if len(im[im>0]) > 0:
        unique,counts = np.unique(im[im > 0],return_counts=True)
        label = unique[counts.argmax()]
    return label

#%%

for t in tqdm(range(15)):
    
    nuc_seg = io.imread(path.join(dirname,f'3d_nuc_seg/cellpose_cleaned_manual/t{t}.tif'))
    cyto_seg = io.imread(path.join(dirname,f'im_seq/t{t}_3d_cyto/t{t}_masks.tif'))
    
    #% Find correspondnence
    
    all_cellposeIDs = np.unique(nuc_seg)[1:]
    
    cellpose_dict = {cellposeID:most_likely_label(_,cyto_seg[nuc_seg == cellposeID]) for cellposeID in all_cellposeIDs}
    cyto_dict = {v:k for k,v in cellpose_dict.items()}
    
    #%
    
    assert(len(all_cellposeIDs) == len(np.unique( cellpose_dict.values() )[0]))
    
    keepIDs = list(cellpose_dict.values())
    
    # Delete the rest
    all_cytoIDs = np.unique(cyto_seg)[1:]
    for cytoID in all_cytoIDs:
        if cytoID not in keepIDs:
            cyto_seg[cyto_seg == cytoID] = 0
        else:
            cyto_seg[cyto_seg == cytoID] = cyto_dict[cytoID]
            
    io.imsave(path.join(dirname,f'3d_cyto_seg/cellpose_cleaned/t{t}.tif'), cyto_seg.astype(np.int16))
    