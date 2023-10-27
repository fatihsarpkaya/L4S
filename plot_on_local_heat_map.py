#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 10:18:51 2023

@author: fatihberkay
"""

import shutil, tarfile

import json

import numpy as np

import matplotlib.pyplot as plt

import pandas as pd

import re

from statistics import mean

import itertools
import seaborn as sns

# slice_name="l4s-fbs6417_0000066146"
# data_dir_tx0 = slice_name + 'singlebottleneck'+"-tx0" #tx0 files stored in a folder whose name is this
# data_dir_tx1 = slice_name + 'singlebottleneck'+"-tx1" #tx1 files stored in a folder whose name is this
# data_dir_tx0 ='l4s-single_queue_FQ-100-fbs6417_0000066146singlebottleneck-tx0_single_queue_FQ'
# data_dir_tx1 ='l4s-single_queue_FQ-100-fbs6417_0000066146singlebottleneck-tx1_single_queue_FQ'


directory="/Users/fatihberkay/Desktop/Single_bottleneck"  #data_dir_tx0 and data_dir_tx1 should be stored here.

#directory = "/Users/ashutoshsrivastava/Downloads/Single_bottleneck"  # directory of the files

exp_factors = {
    'n_bdp': [0.5, 2, 5, 10],  # n x bandwidth delay product
    'btl_capacity': [100, 1000],
    'base_rtt': [10, 50, 100],
    #'aqm': ['FIFO', 'single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2'],
    'aqm': ['single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2'],
    'ecn_threshold': [5, 20],
    'ecn_fallback': [0, 1],  # 0: OFF, 1: ON
    'rx0_ecn': [0, 1, 2],  # 0: noecn, 1: ecn, 2: accecn
    'rx1_ecn': [0, 1, 2],  # 0: noecn, 1: ecn, 2: accecn
    'cc_tx0': ["prague"],
    'cc_tx1': ["cubic"],
    'trial': [1]
}

factor_names = [k for k in exp_factors]
factor_lists = list(itertools.product(*exp_factors.values()))

exp_lists = []

seen_combinations = set()

for factor_l in factor_lists:
    temp_dict = dict(zip(factor_names, factor_l))
    if temp_dict['aqm'] == 'FIFO':
        del temp_dict['ecn_threshold']

    # Convert dict to a frozenset for set operations
    fs = frozenset(temp_dict.items())

    if fs not in seen_combinations:
        seen_combinations.add(fs)
        exp_lists.append(temp_dict)

# remove previously stored data files
# shutil.rmtree(data_dir_tx0)
# shutil.rmtree(data_dir_tx1)

# extract tar files 
# with tarfile.open(data_dir_tx0+'.tgz ', 'r:gz') as tar:
#    tar.extractall()

# with tarfile.open(data_dir_tx1+'.tgz ', 'r:gz') as tar:
#    tar.extractall()

# get all throughput and SRTT data

throughput_data = {}  # Initialize the dictionary

srtt_data = {}

for exp in exp_lists:
    name_tx0 = "%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (
        exp['cc_tx0'], exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'],
        str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])
    name_tx1 = "%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (
        exp['cc_tx1'], exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'],
        str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])

    # Load the JSON output file into a Python object

    ##### Average Throughput for Each Flow ****

    # with open(directory+data_dir_tx0+"/{flow1}-result.json".format(flow1=name_tx0), "r") as f:
    with open(directory + "/{flow1}-result.json".format(flow1=name_tx0), "r") as f:
        iperf3_data = json.load(f)

    throughput_data[name_tx0] = iperf3_data['end']['sum_received']['bits_per_second'] / (1000000 * 1)  # to convert Mbit

    # with open(directory+data_dir_tx1+"/{flow1}-result.json".format(flow1=name_tx1), "r") as f:
    with open(directory + "/{flow1}-result.json".format(flow1=name_tx1), "r") as f:
        iperf3_data = json.load(f)

    throughput_data[name_tx1] = iperf3_data['end']['sum_received']['bits_per_second'] / (1000000 * 1)  # to convert Mbit

    ##### Average SRTT for Each Flow ******

    columns = ['timestamp', 'flow ID', 'cwnd', 'srtt']
    # df_f1= pd.read_csv(directory+data_dir_tx0+'/{flow1}-ss.csv'.format(flow1=name_tx0), names=columns)
    df_f1 = pd.read_csv(directory + '/{flow1}-ss.csv'.format(flow1=name_tx0), names=columns)
    # df_f2= pd.read_csv(directory+data_dir_tx1+'/{flow1}-ss.csv'.format(flow1=name_tx1), names=columns)
    df_f2 = pd.read_csv(directory + '/{flow1}-ss.csv'.format(flow1=name_tx1), names=columns)

    # Filter out rows with flow ID = 4, they are for the control flows
    df_f1 = df_f1[df_f1['flow ID'] != 4]
    df_f2 = df_f2[df_f2['flow ID'] != 4]

    average_RTT_f1 = df_f1['srtt'].mean()
    average_RTT_f2 = df_f2['srtt'].mean()

    srtt_data[name_tx0] = average_RTT_f1
    srtt_data[name_tx1] = average_RTT_f2

# Placeholder: A dictionary to store throughput data for each experiment
# Example format: "n_bdp_btl_capacity_base_rtt_aqm_ecn_threshold_ecn_fallback_rx_ecn_cc_tx_trial"
# throughput_data = {
#     "prague_0.5_100_10_FIFO_none_0_0_0": 55.787676690306085,
#     "prague_2.0_100_10_FIFO_none_0_0_0": 54.248112443427175,
#     "prague_5.0_100_10_FIFO_none_0_0_0": 38.2013028326071,
#     "prague_10.0_100_10_FIFO_none_0_0_0": 63.37023092922114,
#     "cubic_0.5_100_10_FIFO_none_0_0_0": 47.47733567404541,
#     "cubic_2.0_100_10_FIFO_none_0_0_0": 37.5916393558464,
#     "cubic_5.0_100_10_FIFO_none_0_0_0": 65.17600721037583,
#     "cubic_10.0_100_10_FIFO_none_0_0_0": 50.3362326648659,
# }

# User-specified parameters, these are the fixed parameters you choose for plotting 
specified_params = {
    'btl_capacity': 100,
    'n_bdp': 2,
    'base_rtt': 10,
    #'ecn_threshold': 5,
    'ecn_fallback': 0,
    'rx0_ecn': 2,
    'rx1_ecn': 2,
    # 'aqm': 'FIFO'

}

exp_factors['btl_capacity']  # these are 100 and 1000
exp_factors['base_rtt']  # these are 10, 50, 100

factor_x = 'aqm'  # choose which parameter you want to observe
factor_y = 'ecn_threshold'
#factor_y = 'base_rtt'
#factor_y = 'n_bdp'  # choose which parameter you want to observe

# Create nested dictionaries to store data by btl_capacity and base_rtt
relevant_data_tx0 = {}
relevant_data_tx1 = {}

relevant_srtt_data_tx0 = {}
relevant_srtt_data_tx1 = {}

for exp in exp_lists:
    is_relevant = all(
        (k == 'ecn_threshold' and (v == exp.get(k) or exp.get(k) is None)) or
        (k != 'ecn_threshold' and v == exp.get(k)) for k, v in specified_params.items()
    )

    if is_relevant:
        btl = exp['btl_capacity']
        rtt = exp['base_rtt']

        name_tx0 = "%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (
            exp['cc_tx0'], exp['n_bdp'], btl, rtt, exp['aqm'], str(exp.get('ecn_threshold', 'none')),
            exp['ecn_fallback'],
            exp['rx0_ecn'], exp['rx1_ecn'])
        name_tx1 = "%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (
            exp['cc_tx1'], exp['n_bdp'], btl, rtt, exp['aqm'], str(exp.get('ecn_threshold', 'none')),
            exp['ecn_fallback'],
            exp['rx0_ecn'], exp['rx1_ecn'])

        xval = exp[factor_x]
        yval= exp[factor_y]
        # Update relevant_data_tx0
        if name_tx0 in throughput_data:
            if yval not in relevant_data_tx0:
                relevant_data_tx0[yval] = {}
            if xval not in relevant_data_tx0[yval]:
                relevant_data_tx0[yval][xval] = []
            relevant_data_tx0[yval][xval].append(throughput_data[name_tx0])

        # Update relevant_data_tx1
        if name_tx1 in throughput_data:
            if yval not in relevant_data_tx1:
                relevant_data_tx1[yval] = {}
            if xval not in relevant_data_tx1[yval]:
                relevant_data_tx1[yval][xval] = []
            relevant_data_tx1[yval][xval].append(throughput_data[name_tx1])

        # Update relevant_srtt_data_tx0
        if name_tx0 in srtt_data:
            if yval not in relevant_srtt_data_tx0:
                relevant_srtt_data_tx0[yval] = {}
            if xval not in relevant_srtt_data_tx0[yval]:
                relevant_srtt_data_tx0[yval][xval] = []
            relevant_srtt_data_tx0[yval][xval].append(srtt_data[name_tx0])

        # Update relevant_srtt_data_tx1
        if name_tx1 in srtt_data:
            if yval not in relevant_srtt_data_tx1:
                relevant_srtt_data_tx1[yval] = {}
            if xval not in relevant_srtt_data_tx1[yval]:
                relevant_srtt_data_tx1[yval][xval] = []
            relevant_srtt_data_tx1[yval][xval].append(srtt_data[name_tx1])

# Average the throughputs for tx0
for yval, xval_data in relevant_data_tx0.items():
    for xval, throughputs in xval_data.items():
        relevant_data_tx0[yval][xval] = np.mean(throughputs)

# Average the throughputs for tx1
for yval, xval_data in relevant_data_tx1.items():
    for xval, throughputs in xval_data.items():
        relevant_data_tx1[yval][xval] = np.mean(throughputs)

# Average the srtts for tx0
for yval, xval_data in relevant_srtt_data_tx0.items():
    for xval, srtts in xval_data.items():
        relevant_srtt_data_tx0[yval][xval] = np.mean(srtts) - rtt

# Average the srtts for tx1
for yval, xval_data in relevant_srtt_data_tx1.items():
    for xval, srtts in xval_data.items():
        relevant_srtt_data_tx1[yval][xval] = np.mean(srtts) - rtt

# Sort and get values for each btl and rtt combination
sorted_throughputs_tx0 = {}
sorted_throughputs_tx1 = {}
sorted_rtts_tx0 = {}
sorted_rtts_tx1 = {}

for yval in sorted(relevant_data_tx0.keys()):
    sorted_throughputs_tx0[yval] = {}
    sorted_rtts_tx0[yval] = {}
    
    for xval in sorted(relevant_data_tx0[yval].keys()):
        sorted_throughputs_tx0[yval][xval] = relevant_data_tx0[yval].get(xval, 0)
        sorted_rtts_tx0[yval][xval] = relevant_srtt_data_tx0[yval].get(xval, 0)


for yval in sorted(relevant_data_tx1.keys()):
    sorted_throughputs_tx1[yval] = {}
    sorted_rtts_tx1[yval] = {}
    
    for xval in sorted(relevant_data_tx1[yval].keys()):
        sorted_throughputs_tx1[yval][xval] = relevant_data_tx1[yval].get(xval, 0)
        sorted_rtts_tx1[yval][xval] = relevant_srtt_data_tx1[yval].get(xval, 0)




def plot_heatmap_for_fixed_btl(sorted_data_tx0, sorted_data_tx1):
    # Initialize an empty dictionary to hold the heatmap data
    heatmap_data = {}

    # Loop through each rtt value under the fixed bottleneck
    for yval in sorted_data_tx0.keys():
        # Loop through each AQM type
        for aqm in sorted_data_tx0[yval].keys():
            prague_throughput = sorted_data_tx0[yval][aqm]
            cubic_throughput = sorted_data_tx1[yval][aqm]
            share = prague_throughput / (prague_throughput + cubic_throughput)

            if yval not in heatmap_data:
                heatmap_data[yval] = {}

            heatmap_data[yval][aqm] = share

    return heatmap_data


#desired_order = ['FIFO', 'single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2']
desired_order = ['single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2']

# Convert the dictionary to a Pandas DataFrame
df = pd.DataFrame(plot_heatmap_for_fixed_btl(sorted_throughputs_tx0, sorted_throughputs_tx1)).fillna(0)
df = df.reindex(desired_order)

# Generate the heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(df, annot=True, cmap="coolwarm", cbar_kws={'label': 'Prague Throughput Share'}, vmin=0, vmax=1)



title_map = {
    'btl_capacity': lambda: f"{specified_params['btl_capacity']}Mbps-",
    'n_bdp': lambda: f"{specified_params['n_bdp']}BDP-",
    'base_rtt': lambda: f"{specified_params['base_rtt']}ms RTT-",
    'ecn_threshold': lambda: f"ECN_thresh = {specified_params['ecn_threshold']}ms -",
    'rx0_ecn': lambda: f"rx0_ecn:{specified_params['rx0_ecn']}-",
    'rx1_ecn': lambda: f"rx1_ecn:{specified_params['rx1_ecn']}-",
    'ecn_fallback': lambda: f"ecnfallback:{specified_params['ecn_fallback']}"
}

dynamic_title = ''.join(val() for key, val in title_map.items() if key != factor_y)
plt.title(dynamic_title)

plt.xlabel(factor_y, fontsize=14)
plt.ylabel("AQM Types", fontsize=14)
plt.savefig('heatmap_prague_share-'+dynamic_title+'.png', dpi=1200)
plt.show()




