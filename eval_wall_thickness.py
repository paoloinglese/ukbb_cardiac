# Copyright 2019, Wenjia Bai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
import os
import argparse
import pandas as pd
from tqdm import tqdm
import sys
sys.path.insert(0, 'P:\\GitHub')

from ukbb_cardiac.common.cardiac_utils import sa_pass_quality_control, evaluate_wall_thickness


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', default='', required=True)
    parser.add_argument('--output_csv', default='', required=True)
    args = parser.parse_args()

    output_root = os.path.dirname(args.output_csv)
    os.makedirs(output_root, exist_ok=True)

    data_path = args.data_dir
    data_list = sorted(os.listdir(data_path))

    processed_list = []
    for data in tqdm(data_list):
        # print(data)
        data_dir = os.path.join(data_path, data)
        out_dir = os.path.join(output_root, data)

        if os.path.isdir(out_dir):
            continue

        if not os.path.isdir(data_dir):
            continue

        # if os.path.isfile(os.path.join(data_path, '_CHECK_SEG_QC_ED.txt')):
        #     print(data)
        #     print('Segmentation did not pass QC. Skipping.')
        #     continue

        # Fix the section Z=24 for this subject
        if data == '12MN01211_manual_3':
            fix = True
        else:
            fix = False

        # Quality control for segmentation at ED
        # If the segmentation quality is low, evaluation of wall thickness may fail.
        seg_sa_name = '{0}/LVSA_seg_ED.nii.gz'.format(data_dir)  # seg_sa_ED
        if not os.path.exists(seg_sa_name):
            print(data)
            print('File does not exist')
            continue

        if not sa_pass_quality_control(seg_sa_name, fix=fix):
            print(data)
            print('Not pass SA quality control')
            continue

        os.makedirs(out_dir, exist_ok=True)

        # Evaluate myocardial wall thickness
        try:
            evaluate_wall_thickness('{0}/LVSA_seg_ED.nii.gz'.format(data_dir),
                                    '{0}/wall_thickness_ED'.format(out_dir),
                                    fix=fix)
        except:
            continue

        processed_list += [data]

    print('Aggregating results...')

    output_dir = os.path.dirname(args.output_csv)
    processed_list = [str(x) for x in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, str(x)))]

    # Record data
    table_mean = []
    table_median = []
    table_max = []
    table_uq = []
    table_std = []
    table_skew = []
    table_99 = []

    subjects = []

    for data in tqdm(processed_list):

        data_dir = os.path.join(output_dir, str(data))

        if not os.path.exists('{0}/wall_thickness_ED_mean.csv'.format(data_dir)):
            continue

        subjects.append(data)

        if os.path.exists('{0}/wall_thickness_ED_mean.csv'.format(data_dir)):
            df = pd.read_csv('{0}/wall_thickness_ED_mean.csv'.format(data_dir), index_col=0)
            line = df['Thickness'].values
            table_mean += [line]

        if os.path.exists('{0}/wall_thickness_ED_med.csv'.format(data_dir)):
            df = pd.read_csv('{0}/wall_thickness_ED_med.csv'.format(data_dir), index_col=0)
            line = df['Thickness_Med'].values
            table_median += [line]

        if os.path.exists('{0}/wall_thickness_ED_max.csv'.format(data_dir)):
            df = pd.read_csv('{0}/wall_thickness_ED_max.csv'.format(data_dir), index_col=0)
            line = df['Thickness_Max'].values
            table_max += [line]

        if os.path.exists('{0}/wall_thickness_ED_uq.csv'.format(data_dir)):
            df = pd.read_csv('{0}/wall_thickness_ED_uq.csv'.format(data_dir), index_col=0)
            line = df['Thickness_UQ'].values
            table_uq += [line]

        if os.path.exists('{0}/wall_thickness_ED_std.csv'.format(data_dir)):
            df = pd.read_csv('{0}/wall_thickness_ED_std.csv'.format(data_dir), index_col=0)
            line = df['Thickness_Std'].values
            table_std += [line]

        if os.path.exists('{0}/wall_thickness_ED_skew.csv'.format(data_dir)):
            df = pd.read_csv('{0}/wall_thickness_ED_skew.csv'.format(data_dir), index_col=0)
            line = df['Thickness_Kurt'].values
            table_skew += [line]

        if os.path.exists('{0}/wall_thickness_ED_99th.csv'.format(data_dir)):
            df = pd.read_csv('{0}/wall_thickness_ED_99th.csv'.format(data_dir), index_col=0)
            line = df['Thickness_99th'].values
            table_99 += [line]


    # Save wall thickness for all the subjects
    df = pd.DataFrame(table_mean, index=subjects,
                    columns=['WT_AHA_1 (mm)', 'WT_AHA_2 (mm)', 'WT_AHA_3 (mm)',
                            'WT_AHA_4 (mm)', 'WT_AHA_5 (mm)', 'WT_AHA_6 (mm)',
                            'WT_AHA_7 (mm)', 'WT_AHA_8 (mm)', 'WT_AHA_9 (mm)',
                            'WT_AHA_10 (mm)', 'WT_AHA_11 (mm)', 'WT_AHA_12 (mm)',
                            'WT_AHA_13 (mm)', 'WT_AHA_14 (mm)', 'WT_AHA_15 (mm)', 'WT_AHA_16 (mm)',
                            'WT_Global (mm)'])
    df.to_csv(args.output_csv + '_mean.csv')

    # Save wall thickness for all the subjects
    df = pd.DataFrame(table_median, index=subjects,
                    columns=['WT_AHA_1 (mm)', 'WT_AHA_2 (mm)', 'WT_AHA_3 (mm)',
                            'WT_AHA_4 (mm)', 'WT_AHA_5 (mm)', 'WT_AHA_6 (mm)',
                            'WT_AHA_7 (mm)', 'WT_AHA_8 (mm)', 'WT_AHA_9 (mm)',
                            'WT_AHA_10 (mm)', 'WT_AHA_11 (mm)', 'WT_AHA_12 (mm)',
                            'WT_AHA_13 (mm)', 'WT_AHA_14 (mm)', 'WT_AHA_15 (mm)', 'WT_AHA_16 (mm)',
                            'WT_Global (mm)'])
    df.to_csv(args.output_csv + '_median.csv')

    # Save wall thickness for all the subjects
    df = pd.DataFrame(table_max, index=subjects,
                    columns=['WT_AHA_1 (mm)', 'WT_AHA_2 (mm)', 'WT_AHA_3 (mm)',
                            'WT_AHA_4 (mm)', 'WT_AHA_5 (mm)', 'WT_AHA_6 (mm)',
                            'WT_AHA_7 (mm)', 'WT_AHA_8 (mm)', 'WT_AHA_9 (mm)',
                            'WT_AHA_10 (mm)', 'WT_AHA_11 (mm)', 'WT_AHA_12 (mm)',
                            'WT_AHA_13 (mm)', 'WT_AHA_14 (mm)', 'WT_AHA_15 (mm)', 'WT_AHA_16 (mm)',
                            'WT_Global (mm)'])
    df.to_csv(args.output_csv + '_max.csv')

    # Save wall thickness for all the subjects
    df = pd.DataFrame(table_std, index=subjects,
                    columns=['WT_AHA_1 (mm)', 'WT_AHA_2 (mm)', 'WT_AHA_3 (mm)',
                            'WT_AHA_4 (mm)', 'WT_AHA_5 (mm)', 'WT_AHA_6 (mm)',
                            'WT_AHA_7 (mm)', 'WT_AHA_8 (mm)', 'WT_AHA_9 (mm)',
                            'WT_AHA_10 (mm)', 'WT_AHA_11 (mm)', 'WT_AHA_12 (mm)',
                            'WT_AHA_13 (mm)', 'WT_AHA_14 (mm)', 'WT_AHA_15 (mm)', 'WT_AHA_16 (mm)',
                            'WT_Global (mm)'])
    df.to_csv(args.output_csv + '_std.csv')

    # Save wall thickness for all the subjects
    df = pd.DataFrame(table_skew, index=subjects,
                    columns=['WT_AHA_1 (mm)', 'WT_AHA_2 (mm)', 'WT_AHA_3 (mm)',
                            'WT_AHA_4 (mm)', 'WT_AHA_5 (mm)', 'WT_AHA_6 (mm)',
                            'WT_AHA_7 (mm)', 'WT_AHA_8 (mm)', 'WT_AHA_9 (mm)',
                            'WT_AHA_10 (mm)', 'WT_AHA_11 (mm)', 'WT_AHA_12 (mm)',
                            'WT_AHA_13 (mm)', 'WT_AHA_14 (mm)', 'WT_AHA_15 (mm)', 'WT_AHA_16 (mm)',
                            'WT_Global (mm)'])
    df.to_csv(args.output_csv + '_skew.csv')

    # Save wall thickness for all the subjects
    df = pd.DataFrame(table_99, index=subjects,
                    columns=['WT_AHA_1 (mm)', 'WT_AHA_2 (mm)', 'WT_AHA_3 (mm)',
                            'WT_AHA_4 (mm)', 'WT_AHA_5 (mm)', 'WT_AHA_6 (mm)',
                            'WT_AHA_7 (mm)', 'WT_AHA_8 (mm)', 'WT_AHA_9 (mm)',
                            'WT_AHA_10 (mm)', 'WT_AHA_11 (mm)', 'WT_AHA_12 (mm)',
                            'WT_AHA_13 (mm)', 'WT_AHA_14 (mm)', 'WT_AHA_15 (mm)', 'WT_AHA_16 (mm)',
                            'WT_Global (mm)'])
    df.to_csv(args.output_csv + '_99th.csv')
