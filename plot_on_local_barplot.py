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



# slice_name="l4s-fbs6417_0000066146"
#data_dir_tx0 = slice_name + 'singlebottleneck'+"-tx0" #tx0 files stored in a folder whose name is this
#data_dir_tx1 = slice_name + 'singlebottleneck'+"-tx1" #tx1 files stored in a folder whose name is this
#data_dir_tx0 ='l4s-single_queue_FQ-100-fbs6417_0000066146singlebottleneck-tx0_single_queue_FQ'
#data_dir_tx1 ='l4s-single_queue_FQ-100-fbs6417_0000066146singlebottleneck-tx1_single_queue_FQ'



#directory="/Users/fatihberkay/Desktop/L4S_Project/Experiments/"  #data_dir_tx0 and data_dir_tx1 should be stored here.

directory="/Users/fatihberkay/Desktop/Single_bottleneck"  #directory of the files


exp_factors = { 
    'n_bdp': [0.5, 2, 5, 10], # n x bandwidth delay product
    'btl_capacity': [100, 1000],
    'base_rtt': [10, 50, 100],
    'aqm': ['FIFO', 'single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2'],
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
    
    #with open(directory+data_dir_tx0+"/{flow1}-result.json".format(flow1=name_tx0), "r") as f:
    with open(directory+"/{flow1}-result.json".format(flow1=name_tx0), "r") as f:
        iperf3_data = json.load(f)

    throughput_data[name_tx0]  = iperf3_data['end']['sum_received']['bits_per_second']/(1000000*1) # to convert Mbit


    #with open(directory+data_dir_tx1+"/{flow1}-result.json".format(flow1=name_tx1), "r") as f:
    with open(directory+"/{flow1}-result.json".format(flow1=name_tx1), "r") as f:
        iperf3_data = json.load(f)


    throughput_data[name_tx1]  = iperf3_data['end']['sum_received']['bits_per_second']/(1000000*1) # to convert Mbit
    
    ##### Average SRTT for Each Flow ******
    
    columns = ['timestamp', 'flow ID', 'cwnd', 'srtt']
    #df_f1= pd.read_csv(directory+data_dir_tx0+'/{flow1}-ss.csv'.format(flow1=name_tx0), names=columns)
    df_f1= pd.read_csv(directory+'/{flow1}-ss.csv'.format(flow1=name_tx0), names=columns)
    #df_f2= pd.read_csv(directory+data_dir_tx1+'/{flow1}-ss.csv'.format(flow1=name_tx1), names=columns)
    df_f2= pd.read_csv(directory+'/{flow1}-ss.csv'.format(flow1=name_tx1), names=columns)
    
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
    #'btl_capacity': 100,
    'n_bdp': 2,
    #'base_rtt': 50,
    'ecn_threshold': 5,
    'ecn_fallback': 0,
    'rx0_ecn': 2,
    'rx1_ecn': 2,
    #'aqm': 'FIFO'
    
}

exp_factors['btl_capacity'] # these are 100 and 1000
exp_factors['base_rtt'] # these are 10, 50, 100

factor_x = 'aqm'  # choose which parameter you want to observe

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
        
        name_tx0 = "%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (exp['cc_tx0'], exp['n_bdp'], btl, rtt, exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])
        name_tx1 = "%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (exp['cc_tx1'], exp['n_bdp'], btl, rtt, exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])
        
        xval = exp[factor_x]
        
        # Update relevant_data_tx0
        if name_tx0 in throughput_data:
            if btl not in relevant_data_tx0:
                relevant_data_tx0[btl] = {}
            if rtt not in relevant_data_tx0[btl]:
                relevant_data_tx0[btl][rtt] = {}
            if xval not in relevant_data_tx0[btl][rtt]:
                relevant_data_tx0[btl][rtt][xval] = []
            relevant_data_tx0[btl][rtt][xval].append(throughput_data[name_tx0])
        
        # Update relevant_data_tx1
        if name_tx1 in throughput_data:
            if btl not in relevant_data_tx1:
                relevant_data_tx1[btl] = {}
            if rtt not in relevant_data_tx1[btl]:
                relevant_data_tx1[btl][rtt] = {}
            if xval not in relevant_data_tx1[btl][rtt]:
                relevant_data_tx1[btl][rtt][xval] = []
            relevant_data_tx1[btl][rtt][xval].append(throughput_data[name_tx1])

        # Update relevant_srtt_data_tx0
        if name_tx0 in srtt_data:
            if btl not in relevant_srtt_data_tx0:
                relevant_srtt_data_tx0[btl] = {}
            if rtt not in relevant_srtt_data_tx0[btl]:
                relevant_srtt_data_tx0[btl][rtt] = {}
            if xval not in relevant_srtt_data_tx0[btl][rtt]:
                relevant_srtt_data_tx0[btl][rtt][xval] = []
            relevant_srtt_data_tx0[btl][rtt][xval].append(srtt_data[name_tx0])

        # Update relevant_srtt_data_tx1
        if name_tx1 in srtt_data:
            if btl not in relevant_srtt_data_tx1:
                relevant_srtt_data_tx1[btl] = {}
            if rtt not in relevant_srtt_data_tx1[btl]:
                relevant_srtt_data_tx1[btl][rtt] = {}
            if xval not in relevant_srtt_data_tx1[btl][rtt]:
                relevant_srtt_data_tx1[btl][rtt][xval] = []
            relevant_srtt_data_tx1[btl][rtt][xval].append(srtt_data[name_tx1])

# Average the throughputs for tx0
for btl, rtt_data in relevant_data_tx0.items():
    for rtt, xval_data in rtt_data.items():
        for xval, throughputs in xval_data.items():
            relevant_data_tx0[btl][rtt][xval] = np.mean(throughputs)

# Average the throughputs for tx1
for btl, rtt_data in relevant_data_tx1.items():
    for rtt, xval_data in rtt_data.items():
        for xval, throughputs in xval_data.items():
            relevant_data_tx1[btl][rtt][xval] = np.mean(throughputs)

# Average the srtts for tx0
for btl, rtt_data in relevant_srtt_data_tx0.items():
    for rtt, xval_data in rtt_data.items():
        for xval, srtts in xval_data.items():
            relevant_srtt_data_tx0[btl][rtt][xval] = np.mean(srtts)

# Average the srtts for tx1
for btl, rtt_data in relevant_srtt_data_tx1.items():
    for rtt, xval_data in rtt_data.items():
        for xval, srtts in xval_data.items():
            relevant_srtt_data_tx1[btl][rtt][xval] = np.mean(srtts)

# Sort and get values for each btl and rtt combination
sorted_throughputs_tx0 = {}
sorted_throughputs_tx1 = {}
sorted_rtts_tx0 = {}
sorted_rtts_tx1 = {}

for btl in sorted(relevant_data_tx0.keys()):
    sorted_throughputs_tx0[btl] = {}
    sorted_rtts_tx0[btl] = {}
    for rtt in sorted(relevant_data_tx0[btl].keys()):
        sorted_throughputs_tx0[btl][rtt] = {}
        sorted_rtts_tx0[btl][rtt] = {}
        
        # Sort xvals
        xvals = sorted(relevant_data_tx0[btl][rtt].keys())
        
        # Get throughputs and rtts for sorted xvals
        sorted_throughputs_tx0[btl][rtt] = {xval: relevant_data_tx0[btl][rtt].get(xval, 0) for xval in xvals}
        sorted_rtts_tx0[btl][rtt] = {xval: relevant_srtt_data_tx0[btl][rtt].get(xval, 0) for xval in xvals}
        
for btl in sorted(relevant_data_tx1.keys()):
    sorted_throughputs_tx1[btl] = {}
    sorted_rtts_tx1[btl] = {}
    for rtt in sorted(relevant_data_tx1[btl].keys()):
        sorted_throughputs_tx1[btl][rtt] = {}
        sorted_rtts_tx1[btl][rtt] = {}
        
        # Sort xvals
        xvals = sorted(relevant_data_tx1[btl][rtt].keys())
        
        # Get throughputs and rtts for sorted xvals
        sorted_throughputs_tx1[btl][rtt] = {xval: relevant_data_tx1[btl][rtt].get(xval, 0) for xval in xvals}
        sorted_rtts_tx1[btl][rtt] = {xval: relevant_srtt_data_tx1[btl][rtt].get(xval, 0) for xval in xvals}

# Define a function to plot a bar graph
# Define a function to plot a bar graph
def plot_bar(subplt, xvals, yvals0, yvals1, label0, label1, xlabel, ylabel, title):
    bar_width = 0.35
    index = np.arange(len(xvals))
    
    bar1 = subplt.bar(index, yvals0, bar_width, label=label0, alpha=0.8, color='b')
    bar2 = subplt.bar(index + bar_width, yvals1, bar_width, label=label1, alpha=0.8, color='r')
    
    subplt.set_xlabel(xlabel)
    subplt.set_ylabel(ylabel)
    subplt.set_title(title)
    subplt.set_xticks(index + bar_width/2)
    subplt.set_xticklabels(xvals)
    subplt.legend()

# Create a function for generating subplots
def create_subplots(sorted_data_tx0, sorted_data_tx1, ylabel, label0, label1):
    num_btl = len(sorted_data_tx0.keys())
    num_rtt = len(sorted_data_tx0[next(iter(sorted_data_tx0))].keys())
    total_plots = num_btl * num_rtt
    grid_rows = int(total_plots**0.5)
    grid_cols = -(-total_plots // grid_rows)  # Ceiling division

    plt.figure(figsize=(25, 20))

    plot_index = 1
    for btl in sorted_data_tx0.keys():
        for rtt in sorted_data_tx0[btl].keys():
            xvals = sorted(sorted_data_tx0[btl][rtt].keys())
            yvals0 = [sorted_data_tx0[btl][rtt].get(xval, 0) for xval in xvals]
            yvals1 = [sorted_data_tx1[btl][rtt].get(xval, 0) for xval in xvals]

            subplt = plt.subplot(grid_rows, grid_cols, plot_index)
            title = f'btl: {btl} Mbps, rtt: {rtt} ms'
            plot_bar(subplt, xvals, yvals0, yvals1, label0, label1, factor_x, ylabel, title)

            plot_index += 1


# Generate subplots for throughput
create_subplots(sorted_throughputs_tx0, sorted_throughputs_tx1, 'Average Throughput (Mbps)', 'TX0 (Prague)', 'TX1 (Cubic)')
plt.xlabel("BDP")
plt.ylabel("Average Throughput (Mbps)")
plt.suptitle('Average Throughput vs Queue Type - '+str(specified_params['n_bdp'])+'BDP-'+str(specified_params['ecn_threshold'])+'ms ECN-'+'rx0_ecn:'+str(specified_params['rx0_ecn'])+'-'+'rx1_ecn:'+str(specified_params['rx1_ecn'])+'-'+'ecnfallback:'+str(specified_params['ecn_fallback']), fontsize=20, y=0.99)
plt.tight_layout()
plt.savefig('barplot_throughput.png', dpi=1200)
plt.show()

# Generate subplots for RTT
create_subplots(sorted_rtts_tx0, sorted_rtts_tx1, 'Average SRTT (ms)', 'TX0 (Prague)', 'TX1 (Cubic)')
plt.xlabel("BDP")
plt.ylabel("Average SRTT (ms)")
plt.suptitle('Average SRTT vs Queue Type - '+str(specified_params['n_bdp'])+'BDP-'+str(specified_params['ecn_threshold'])+'ms ECN-'+'rx0_ecn:'+str(specified_params['rx0_ecn'])+'-'+'rx1_ecn:'+str(specified_params['rx1_ecn'])+'-'+'ecnfallback:'+str(specified_params['ecn_fallback']), fontsize=20, y=0.99)
plt.tight_layout()
plt.savefig('barplot_srtt.png', dpi=1200)
plt.show()