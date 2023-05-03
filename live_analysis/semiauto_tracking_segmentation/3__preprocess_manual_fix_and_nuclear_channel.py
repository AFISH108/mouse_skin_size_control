#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 12:22:31 2021

@author: xies
"""

import numpy as np
import pandas as pd
import matplotlib.pylab as plt

from skimage import io, measure, exposure, util, filters
import seaborn as sb
from os import path
from tqdm import tqdm
from scipy import ndimage


from basicUtils import draw_gate,gate_on_selector

# dirnames = {}
# dirnames['WT R2'] = '/Users/xies//OneDrive - Stanford/Skin/Two photon/NMS/06-25-2022/M1 WT/R1/'
dirname = '/Users/xies/OneDrive - Stanford/Skin/Two photon/NMS/09-29-2022 RB-KO pair/WT/R2'

# dirnames['RBKO R1'] = '/Users/xies/OneDrive - Stanford/Skin/Two photon/NMS/09-29-2022 RB-KO pair/RBKO/R1'
# dirnames['RBKO R2'] = '/Users/xies/OneDrive - Stanford/Skin/Two photon/NMS/09-29-2022 RB-KO pair/RBKO/R2'

dx = 0.2920097/1.5
# dx = 1

OVERWRITE = True

dist2expand = 3


#%% Calculate CLAHE and threshold masks

for name,dirname in dirnames.items():
    
    print(f'--- Working on {name} ---')
    
    genotype = name.split(' ')[0]
    
    # if not path.exists(path.join(dirname,f'manual_tracking/manual_tracking_final_exp{dist2expand}.tiff')):
    #     manual_segs = io.imread(path.join(dirname,'manual_tracking/manual_tracking_final.tiff'))
        # print('Generating expanded labels')
        # for t in tqdm(range(manual_segs.shape[0])):
        #     manual_segs[t,...] = segmentation.expand_labels(manual_segs[t,...],distance=dist2expand)     
        # io.imsave(path.join(dirname,f'manual_tracking/manual_tracking_final_exp{dist2expand}.tiff'),manual_segs)
    
    G = io.imread(path.join(dirname,'master_stack/G.tif'))
    for t,im in enumerate(G):
        G[t,...] = ndimage.gaussian_filter(im,sigma=1)
    
    G_th = np.zeros_like(G,dtype=bool)
    
    kernel_size = (G.shape[1] // 3,
                   G.shape[2] // 8,
                   G.shape[3] // 8)
    kernel_size = np.array(kernel_size)
    
    if not path.exists(path.join(dirname,'master_stack/G_clahe.tif')) or OVERWRITE:
        G_clahe = np.zeros_like(G,dtype=float)
        print('Calculating CLAHE de novo and slice-by-slice threshold masks')
        for t, im_time in tqdm(enumerate(G)):
            G_clahe[t,...] = exposure.equalize_adapthist(im_time, kernel_size=kernel_size, clip_limit=0.01, nbins=256)
            for z, im in enumerate(G_clahe[t,...]):
                G_th[t,z,...] = im > filters.threshold_otsu(im)
        io.imsave(path.join(dirname,'master_stack/G_clahe.tif'),util.img_as_uint(G_clahe))
    else:
        print('Loaded CLAHE and calculating slice-by-slice threshold masks')
        G_clahe = io.imread(path.join(dirname,'master_stack/G_clahe.tif'))
        for t, im_time in tqdm(enumerate(G)):
            for z, im in enumerate(G_clahe[t,...]):
                G_th[t,z,...] = im > filters.threshold_otsu(im)
                
    io.imsave(path.join(dirname,'master_stack/G_clahe_th.tif'),G_th)
    
#%% Renormalize each movie frame

dirname = '/Users/xies/OneDrive - Stanford/Skin/Two photon/NMS/09-29-2022 RB-KO pair/RBKO/R2'

im = io.imread(path.join(dirname,'master_stack/R.tif'))

_tmp = []
for t in tqdm(range(16)):
    #@todo: load R channel to get FUCCI-high cells
    # im = io.imread(path.join(dirname,f'im_seq/t{t}.tif'))
    basal_seg = io.imread(path.join(dirname,f'cellpose_pruned/t{t}_manual.tif'))
    R = im[t,...]
    
    this_frame = pd.DataFrame(measure.regionprops_table(basal_seg,intensity_image=R, properties=['area','label','intensity_mean']))
    this_frame['Frame'] = t
    _tmp.append(this_frame)
    
frame_averages = pd.concat(_tmp)
frame_averages.to_csv(path.join(dirname,'frame_averages.csv'))

#%%

real_selector = draw_gate(frame_averages,x='area',y='intensity_mean',alpha=0.05)

#%%

I = gate_on_selector(real_selector,frame_averages,'area','intensity_mean')
real_cells = frame_averages[I]

real_cells.to_csv(path.join(dirname,'real_cells_avg_size.csv'))

#%%
real_cells['FUCCI thresh'] = 'Low'
fucci_high_selector = draw_gate(real_cells,x='area',y='intensity_mean',alpha=0.05)

#%%
I = gate_on_selector(fucci_high_selector,real_cells,'area','intensity_mean')
real_cells.loc[I,'FUCCI thresh'] = 'High'

high_fucci = real_cells[real_cells['FUCCI thresh'] == 'High']

high_fucci.to_csv(path.join(dirname,'high_fucci_avg_size.csv'))

#%%

plt.plot(frame_averages.groupby('Frame').mean()['area'])
plt.plot(real_cells.groupby('Frame').mean()['area'])
plt.plot(high_fucci.groupby('Frame').mean()['area'])





  