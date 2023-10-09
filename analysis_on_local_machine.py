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



slice_name="l4s-fbs6417_0000066146"

data_dir_tx0 = slice_name + 'singlebottleneck'+"-tx0" #tx0 files stored in a folder whose name is this
data_dir_tx1 = slice_name + 'singlebottleneck'+"-tx1" #tx1 files stored in a folder whose name is this

directory="/Users/fatihberkay/Desktop/L4S_Project/Experiments/"  #data_dir_tx0 and data_dir_tx1 should be stored here.


exp_factors = { 
    'n_bdp': [0.5, 2, 5, 10], # n x bandwidth delay product
    'btl_capacity': [100], # 'btl_capacity': [100, 1000],
    'base_rtt': [10, 50, 100],
    'aqm': ['FIFO'], # 'aqm': ['FIFO', 'single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2'],
    'ecn_threshold': [5, 20],
    'ecn_fallback': [0, 1], # 0: OFF, 1: ON
    'rx0_ecn': [0, 1, 2], # 0: noecn, 1: ecn, 2: accecn
    'rx1_ecn': [0, 1, 2], # 0: noecn, 1: ecn, 2: accecn
    'cc_tx0' : ["prague"],
    'cc_tx1' : ["cubic"],
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
#shutil.rmtree(data_dir_tx0)
#shutil.rmtree(data_dir_tx1)

# extract tar files 
#with tarfile.open(data_dir_tx0+'.tgz ', 'r:gz') as tar:
#    tar.extractall()
    
#with tarfile.open(data_dir_tx1+'.tgz ', 'r:gz') as tar:
#    tar.extractall()



#get all throughput and SRTT data

throughput_data = {}  # Initialize the dictionary

srtt_data = {}

for exp in exp_lists:

    name_tx0="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (exp['cc_tx0'],exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])
    name_tx1="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (exp['cc_tx1'],exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])
    

    # Load the JSON output file into a Python object
    
    ##### Average Throughput for Each Flow ****
    
    with open(directory+data_dir_tx0+"/{flow1}-result.json".format(flow1=name_tx0), "r") as f:
        iperf3_data = json.load(f)

    throughput_data[name_tx0]  = iperf3_data['end']['sum_received']['bits_per_second']/(1000000*1) # to convert Mbit


    with open(directory+data_dir_tx1+"/{flow1}-result.json".format(flow1=name_tx1), "r") as f:
        iperf3_data = json.load(f)


    throughput_data[name_tx1]  = iperf3_data['end']['sum_received']['bits_per_second']/(1000000*1) # to convert Mbit
    
    
    
    ##### Average SRTT for Each Flow ******
    
    columns = ['timestamp', 'flow ID', 'cwnd', 'srtt']
    df_f1= pd.read_csv(directory+data_dir_tx0+'/{flow1}-ss.csv'.format(flow1=name_tx0), names=columns)
    df_f2= pd.read_csv(directory+data_dir_tx1+'/{flow1}-ss.csv'.format(flow1=name_tx1), names=columns)
    
    # Filter out rows with flow ID = 4, they are for the control flows
    df_f1= df_f1[df_f1['flow ID'] != 4]
    df_f2= df_f2[df_f2['flow ID'] != 4]
    
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
    'ecn_threshold': 5,
    #'ecn_fallback': 0,
    'rx0_ecn': 0,
    'rx1_ecn': 0,
    'aqm': 'FIFO'
    
}

factor_x = 'ecn_fallback' # choose which parameter you want to observe

relevant_data_tx0 = {}
relevant_data_tx1 = {}

relevant_srtt_data_tx0 = {}
relevant_srtt_data_tx1 = {}

for exp in exp_lists:
    #is_relevant = all(item in exp.items() for item in specified_params.items())
    
    is_relevant = all(
        (k == 'ecn_threshold' and (v == exp.get(k) or exp.get(k) is None)) or 
        (k != 'ecn_threshold' and v == exp.get(k)) for k, v in specified_params.items()
    )

    if is_relevant:
        name_tx0="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (exp['cc_tx0'],exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])
        name_tx1="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (exp['cc_tx1'],exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])

        print(exp[factor_x])
        if name_tx0 in throughput_data:
            xval = exp[factor_x]
            if xval not in relevant_data_tx0:
                relevant_data_tx0[xval] = []
            relevant_data_tx0[xval].append(throughput_data[name_tx0])
            
        if name_tx1 in throughput_data:
            xval = exp[factor_x]
            if xval not in relevant_data_tx1:
                relevant_data_tx1[xval] = []
            relevant_data_tx1[xval].append(throughput_data[name_tx1])
            
        if name_tx0 in srtt_data:
            xval = exp[factor_x]
            if xval not in relevant_srtt_data_tx0:
                relevant_srtt_data_tx0[xval] = []
            relevant_srtt_data_tx0[xval].append(srtt_data[name_tx0])
            
        if name_tx1 in srtt_data:
            xval = exp[factor_x]
            if xval not in relevant_srtt_data_tx1:
                relevant_srtt_data_tx1[xval] = []
            relevant_srtt_data_tx1[xval].append(srtt_data[name_tx1])
            
        

# Average the throughputs over all trials for each n_bdp
for xval, throughputs in relevant_data_tx0.items():
    relevant_data_tx0[xval] = np.mean(throughputs)
    
for xval, throughputs in relevant_data_tx1.items():
    relevant_data_tx1[xval] = np.mean(throughputs)
    
for xval, srtts in relevant_srtt_data_tx0.items():
    relevant_srtt_data_tx0[xval] = np.mean(srtts)
    
for xval, srtts in relevant_srtt_data_tx1.items():
    relevant_srtt_data_tx1[xval] = np.mean(srtts)


# Sort values
xvals = sorted(list(set(list(relevant_data_tx0.keys()) + list(relevant_data_tx1.keys()))))

print(xvals)

# Get throughputs for sorted values
throughputs_tx0 = [relevant_data_tx0.get(xval, 0) for xval in xvals]
throughputs_tx1 = [relevant_data_tx1.get(xval, 0) for xval in xvals]

rtts_tx0 = [relevant_srtt_data_tx0.get(xval, 0) for xval in xvals]
rtts_tx1 = [relevant_srtt_data_tx1.get(xval, 0) for xval in xvals]

print(rtts_tx0)
print(rtts_tx1)
bar_width = 0.35
index = np.arange(len(xvals))

plt.figure(figsize=(10,6))
bar1 = plt.bar(index, throughputs_tx0, bar_width, label='TX0', alpha=0.8, color='b')
bar2 = plt.bar(index + bar_width, throughputs_tx1, bar_width, label='TX1', alpha=0.8, color='r')

# Annotate bars for TX0
for bar in bar1:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, f"{height:.2f}", ha='center', va='bottom')

# Annotate bars for TX1
for bar in bar2:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, f"{height:.2f}", ha='center', va='bottom')

# Label the bars and the x-axis
plt.rcParams['figure.dpi'] = 300
plt.xlabel(factor_x)
plt.ylabel('Average Throughput')
plt.title('Average Throughput vs queue type for different flows')
plt.xticks(index + bar_width/2, xvals)  # Positioning on the x axis
plt.legend()
plt.tight_layout()
plt.savefig('fig1.png', dpi=1200)

plt.show()



bar_width = 0.35
index = np.arange(len(xvals))

plt.figure(figsize=(10,6))
bar1 = plt.bar(index, rtts_tx0, bar_width, label='TX0', alpha=0.8, color='b')
bar2 = plt.bar(index + bar_width, rtts_tx1, bar_width, label='TX1', alpha=0.8, color='r')

# Annotate bars for TX0
for bar in bar1:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, f"{height:.2f}", ha='center', va='bottom')

# Annotate bars for TX1
for bar in bar2:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, f"{height:.2f}", ha='center', va='bottom')

# Label the bars and the x-axis
plt.rcParams['figure.dpi'] = 300
plt.xlabel(factor_x)
plt.ylabel('Average SRTT')
plt.title('Average SRTT vs queue type for different flows')
plt.xticks(index + bar_width/2, xvals)  # Positioning on the x axis
plt.legend()
plt.tight_layout()
plt.savefig('fig2.png', dpi=1200)

plt.show()
