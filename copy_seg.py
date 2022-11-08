import os
import os.path as osp
import shutil
from tqdm import tqdm
import pandas as pd


source_dir = 'S:\\DL_segmentation\\3D_HCM_atlas_targets'
target_dir = 'P:\\hcm-wt-16-aha'

metadata = pd.read_csv('P:\\mesh-dim-red\\HCM-609\\data\\metadata_hcm.csv')
ID = metadata['ID'].values

dirs = os.listdir(source_dir)
subjects_from_dirs = [x.split('_')[0] for x in dirs]
hcm_dirs = [dirs[i] for i in range(len(dirs)) if subjects_from_dirs[i] in ID]

for d in tqdm(hcm_dirs):

    subj_dir = osp.join(source_dir, d)
    if not osp.isdir(subj_dir):
        raise IOError('Dir not found')

    if not osp.isfile(osp.join(subj_dir, 'seg_lvsa_SR_ED.nii.gz')):
        raise FileNotFoundError('File not found')

    os.makedirs(osp.join(target_dir, d), exist_ok=True)
    shutil.copy(osp.join(subj_dir, 'seg_lvsa_SR_ED.nii.gz'), osp.join(target_dir, d))
