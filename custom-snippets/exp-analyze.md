
::: {.cell .markdown}
### Analysis of the results
:::

::: {.cell .code}
```python
for exp in exp_lists:
    name_tx0="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d_%d" % (exp['cc_tx0'],exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'], exp['trial'])
    name_tx1="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d_%d" % (exp['cc_tx1'],exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'], exp['trial'])
    
    
    file_out_tx0_csv = name_tx0+"-ss.csv"
    stdout_tx0_csv, stderr_tx0_csv = tx0_node.execute("ls " + file_out_tx0_csv, quiet=True) 
    
    file_out_tx1_csv = name_tx1+"-ss.csv"
    stdout_tx1_csv, stderr_tx1_csv = tx1_node.execute("ls " + file_out_tx1_csv, quiet=True) 

    if len(stdout_tx0_csv) and len(stdout_tx1_csv):
        print("Already have " + name_tx0 + " and "+ name_tx1 + ", skipping")

    elif len(stderr_tx0_csv) or len(stderr_tx1_csv):
        print("Running to generate csv files " + name_tx0 + " and "+ name_tx1)
    
        ss_tx0_script_processing="""

        f_1={types}; 
        rm -f ${{f_1}}-ss.csv;
        cat ${{f_1}}-ss.txt | sed -e ":a; /<->$/ {{ N; s/<->\\n//; ba; }}"  | grep "iperf3" | grep -v "SYN-SENT"> ${{f_1}}-ss-processed.txt; 
        cat ${{f_1}}-ss-processed.txt | awk '{{print $1}}' > ts-${{f_1}}.txt; 
        cat ${{f_1}}-ss-processed.txt | grep -oP '\\bcwnd:.*?(\s|$)' | awk -F '[:,]' '{{print $2}}' | tr -d ' ' > cwnd-${{f_1}}.txt; 
        cat ${{f_1}}-ss-processed.txt | grep -oP '\\brtt:.*?(\s|$)' | awk -F '[:,]' '{{print $2}}' | tr -d ' '  | cut -d '/' -f 1   > srtt-${{f_1}}.txt; 
        cat ${{f_1}}-ss-processed.txt | grep -oP '\\bfd=.*?(\s|$)' | awk -F '[=,]' '{{print $2}}' | tr -d ')' | tr -d ' '   > fd-${{f_1}}.txt;
        paste ts-${{f_1}}.txt fd-${{f_1}}.txt cwnd-${{f_1}}.txt srtt-${{f_1}}.txt -d ',' > ${{f_1}}-ss.csv;""".format(types=name_tx0)
     
        tx0_node.execute(ss_tx0_script_processing)

        ss_tx1_script_processing="""

        f_2={types};
        rm -f ${{f_2}}-ss.csv;
        cat ${{f_2}}-ss.txt | sed -e ":a; /<->$/ {{ N; s/<->\\n//; ba; }}"  | grep "iperf3" | grep -v "SYN-SENT" > ${{f_2}}-ss-processed.txt; 
        cat ${{f_2}}-ss-processed.txt | awk '{{print $1}}' > ts-${{f_2}}.txt; 
        cat ${{f_2}}-ss-processed.txt | grep -oP '\\bcwnd:.*?(\s|$)' |  awk -F '[:,]' '{{print $2}}' | tr -d ' ' > cwnd-${{f_2}}.txt; 
        cat ${{f_2}}-ss-processed.txt | grep -oP '\\brtt:.*?(\s|$)' |  awk -F '[:,]' '{{print $2}}' | tr -d ' '  | cut -d '/' -f 1   > srtt-${{f_2}}.txt; 
        cat ${{f_2}}-ss-processed.txt | grep -oP '\\bfd=.*?(\s|$)' |  awk -F '[=,]' '{{print $2}}' | tr -d ')' | tr -d ' '   > fd-${{f_2}}.txt;
        paste ts-${{f_2}}.txt fd-${{f_2}}.txt cwnd-${{f_2}}.txt srtt-${{f_2}}.txt -d ',' > ${{f_2}}-ss.csv;""".format(types=name_tx1)


        tx1_node.execute(ss_tx1_script_processing)


tx0_node.execute('mkdir '+data_dir_tx0)

tx0_node.execute('mv *.json '+ data_dir_tx0)
tx0_node.execute('mv *.txt '+ data_dir_tx0)
tx0_node.execute('mv *.csv '+ data_dir_tx0)

tx0_node.execute('tar -czvf '+data_dir_tx0+ '.tgz ' +  data_dir_tx0)


tx1_node.execute('mkdir '+data_dir_tx1)

tx1_node.execute('mv *.json '+ data_dir_tx1)
tx1_node.execute('mv *.txt '+ data_dir_tx1)
tx1_node.execute('mv *.csv '+ data_dir_tx1)
        
tx1_node.execute('tar -czvf '+data_dir_tx1+ '.tgz ' +  data_dir_tx1)
```
:::

::: {.cell .code}
```python
slice_name_str = repr(slice_name)

content_tx0 = f"""
# generate full factorial experiment
import itertools
import json
import pandas as pd

exp_lists = {exp_lists}
slice_name = {slice_name_str}

data_dir_tx0 = slice_name + 'singlebottleneck' + "-tx0"

throughput_data = {{}}  # Initialize the dictionary
srtt_data = {{}}

for exp in exp_lists:
    name_tx0 = "%s_%0.1f_%d_%d_%s_%s_%d_%d_%d_%d" % (exp['cc_tx0'], exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'], exp['trial'])

    # Load the JSON output file into a Python object
    with open(f"/home/ubuntu/{{data_dir_tx0}}/{{name_tx0}}-result.json") as f:
        iperf3_data = json.load(f)

    throughput_data[name_tx0] = iperf3_data['end']['sum_received']['bits_per_second'] / (1000000 * 1)  # to convert Mbit

    # Average SRTT for Each Flow
    columns = ['timestamp', 'flow ID', 'cwnd', 'srtt']
    df_f1 = pd.read_csv(f"/home/ubuntu/{{data_dir_tx0}}/{{name_tx0}}-ss.csv", names=columns)

    # Filter out rows with flow ID = 4, they are for the control flows
    df_f1 = df_f1[df_f1['flow ID'] != 4]

    average_RTT_f1 = df_f1['srtt'].mean()
    srtt_data[name_tx0] = average_RTT_f1

# Save throughput_data to a JSON file
with open('throughput_data.json', 'w') as f:
    json.dump(throughput_data, f)

# Save srtt_data to a JSON file
with open('srtt_data.json', 'w') as f:
    json.dump(srtt_data, f)
"""

content_tx1 = f"""
# generate full factorial experiment
import itertools
import json
import pandas as pd

exp_lists = {exp_lists}
slice_name = {slice_name_str}

data_dir_tx1 = slice_name + 'singlebottleneck' + "-tx1"

throughput_data = {{}}  # Initialize the dictionary
srtt_data = {{}}

for exp in exp_lists:
    name_tx1 = "%s_%0.1f_%d_%d_%s_%s_%d_%d_%d_%d" % (exp['cc_tx1'], exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'], exp['trial'])

    # Load the JSON output file into a Python object
    with open(f"/home/ubuntu/{{data_dir_tx1}}/{{name_tx1}}-result.json") as f:
        iperf3_data = json.load(f)

    throughput_data[name_tx1] = iperf3_data['end']['sum_received']['bits_per_second'] / (1000000 * 1)  # to convert Mbit

    # Average SRTT for Each Flow
    columns = ['timestamp', 'flow ID', 'cwnd', 'srtt']
    df_f1 = pd.read_csv(f"/home/ubuntu/{{data_dir_tx1}}/{{name_tx1}}-ss.csv", names=columns)

    # Filter out rows with flow ID = 4, they are for the control flows
    df_f1 = df_f1[df_f1['flow ID'] != 4]

    average_RTT_f1 = df_f1['srtt'].mean()
    srtt_data[name_tx1] = average_RTT_f1

# Save throughput_data to a JSON file
with open('throughput_data.json', 'w') as f:
    json.dump(throughput_data, f)

# Save srtt_data to a JSON file
with open('srtt_data.json', 'w') as f:
    json.dump(srtt_data, f)
"""

tx0_file_path = 'analysis_tx0.py'
tx1_file_path = 'analysis_tx1.py'

# Write the content to the new file
with open(tx0_file_path, 'w') as new_file:
    new_file.write(content_tx0)

print(f"Content written to {tx0_file_path}")

with open(tx1_file_path, 'w') as new_file:
    new_file.write(content_tx1)

print(f"Content written to {tx1_file_path}")
```
:::

::: {.cell .code}
```python
tx0_node.upload_file("/home/fabric/work/analysis_tx0.py","/home/ubuntu/analysis_tx0.py")
tx1_node.upload_file("/home/fabric/work/analysis_tx1.py","/home/ubuntu/analysis_tx1.py")

cmds_py_install = '''
            sudo apt-get -y install python3
            sudo apt -y install python3-pip
            pip install numpy
            pip install matplotlib
            pip install pandas
            '''

tx0_node.execute(cmds_py_install)
tx1_node.execute(cmds_py_install)
```
:::

::: {.cell .code}
```python
tx0_node.execute('python3 analysis_tx0.py')
tx1_node.execute('python3 analysis_tx1.py')
```
:::

::: {.cell .code}
```python
tx0_node.download_file("/home/fabric/work/tput_tx0.json","/home/ubuntu/throughput_data.json")
tx0_node.download_file("/home/fabric/work/srtt_tx0.json","/home/ubuntu/srtt_data.json")

tx1_node.download_file("/home/fabric/work/tput_tx1.json","/home/ubuntu/throughput_data.json")
tx1_node.download_file("/home/fabric/work/srtt_tx1.json","/home/ubuntu/srtt_data.json")
```
:::

::: {.cell .code}
```python

import json
import os

# Initialize empty variables
throughput_data = {}
srtt_data = {}

# Directory containing JSON files
data_directory = '/home/fabric/work/'

# List of JSON files in the directory
json_files = [f for f in os.listdir(data_directory) if f.endswith('.json')]

# Load data from each JSON file and update the variables
for file_name in json_files:
    file_path = os.path.join(data_directory, file_name)
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Check if the file contains throughput data or srtt data based on its name
    if 'tput' in file_name:
        throughput_data.update(data)
    elif 'srtt' in file_name:
        srtt_data.update(data)
```
:::

::: {.cell .code}
```python

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

def plot_heatmap_for_rtt(sorted_data_tx0, sorted_data_tx1):
    # Initialize an empty dictionary to hold the heatmap data
    heatmap_data = {}

    # Loop through each rtt value under the fixed bottleneck
    for yval in sorted_data_tx0.keys():
        # Loop through each AQM type
        for aqm in sorted_data_tx0[yval].keys():
            prague_rtt = sorted_data_tx0[yval][aqm]
            cubic_rtt = sorted_data_tx1[yval][aqm]
            cubic_relative_diff = (cubic_rtt - prague_rtt) / cubic_rtt

            if yval not in heatmap_data:
                heatmap_data[yval] = {}

            heatmap_data[yval][aqm] = cubic_relative_diff

    return heatmap_data

!pip install seaborn
```
:::

::: {.cell .code}
```python

import shutil, tarfile

import json

import numpy as np

import matplotlib.pyplot as plt

import pandas as pd

import re

from statistics import mean

import itertools

import seaborn as sns

import os
from itertools import product
from matplotlib.colors import ListedColormap

specified_params1 = {
    'btl_capacity': [100],
    #'n_bdp': [0.5, 2, 5, 10],
    'base_rtt': [5, 10, 50], 
    'ecn_threshold': [1, 5],
    'ecn_fallback': [0], 
    'rx0_ecn': [2],
    'rx1_ecn': [1],
    # 'aqm': 'FIFO'

}

keys = specified_params1.keys() 
values = (specified_params1[key] for key in keys)
combinations = [dict(zip(keys, combination)) for combination in product(*values)]

exp_factors['btl_capacity'] 
exp_factors['base_rtt']  

factor_x = 'aqm'  # choose which parameter you want to observe
factor_y = 'n_bdp'  # choose which parameter you want to observe

# Create nested dictionaries to store data by btl_capacity and base_rtt

fig1, axes1 = plt.subplots(2, 3, figsize=(53, 30))
fig2, axes2 = plt.subplots(2, 3, figsize=(53, 30)) # Adjust the figsize as needed

for index, i in enumerate(combinations):
    specified_params=i
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
    
            name_tx0 = "%s_%0.1f_%d_%d_%s_%s_%d_%d_%d_%d" % (
                exp['cc_tx0'], exp['n_bdp'], btl, rtt, exp['aqm'], str(exp.get('ecn_threshold', 'none')),
                exp['ecn_fallback'],
                exp['rx0_ecn'], exp['rx1_ecn'], exp['trial'])
            name_tx1 = "%s_%0.1f_%d_%d_%s_%s_%d_%d_%d_%d" % (
                exp['cc_tx1'], exp['n_bdp'], btl, rtt, exp['aqm'], str(exp.get('ecn_threshold', 'none')),
                exp['ecn_fallback'],
                exp['rx0_ecn'], exp['rx1_ecn'], exp['trial'])
    
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
                relevant_srtt_data_tx0[yval][xval].append(srtt_data[name_tx0]-rtt)
    
            # Update relevant_srtt_data_tx1
            if name_tx1 in srtt_data:
                if yval not in relevant_srtt_data_tx1:
                    relevant_srtt_data_tx1[yval] = {}
                if xval not in relevant_srtt_data_tx1[yval]:
                    relevant_srtt_data_tx1[yval][xval] = []
                relevant_srtt_data_tx1[yval][xval].append(srtt_data[name_tx1]-rtt)

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
            relevant_srtt_data_tx0[yval][xval] = np.mean(srtts) 
    
    # Average the srtts for tx1
    for yval, xval_data in relevant_srtt_data_tx1.items():
        for xval, srtts in xval_data.items():
            relevant_srtt_data_tx1[yval][xval] = np.mean(srtts)
    
    # Sort and get values for each btl and rtt combination
    sorted_throughputs_tx0 = {}
    sorted_throughputs_tx1 = {}
    sorted_rtts_tx0 = {}
    sorted_rtts_tx1 = {}
    
    for yval in sorted(relevant_data_tx0.keys()):
        sorted_throughputs_tx0[yval] = {}
        sorted_rtts_tx0[yval] = {}
        
        for xval in sorted(relevant_data_tx0[yval].keys()):
            sorted_throughputs_tx0[yval][xval] = relevant_data_tx0[yval].get(xval, None)
            sorted_rtts_tx0[yval][xval] = relevant_srtt_data_tx0[yval].get(xval, None)
    
    
    for yval in sorted(relevant_data_tx1.keys()):
        sorted_throughputs_tx1[yval] = {}
        sorted_rtts_tx1[yval] = {}
        
        for xval in sorted(relevant_data_tx1[yval].keys()):
            sorted_throughputs_tx1[yval][xval] = relevant_data_tx1[yval].get(xval, None)
            sorted_rtts_tx1[yval][xval] = relevant_srtt_data_tx1[yval].get(xval, None)
    
    
    title_map = {
    'btl_capacity': lambda: f"{specified_params['btl_capacity']}Mbps-",
    'n_bdp': lambda: f"{specified_params['n_bdp']}BDP-",
    'base_rtt': lambda: f"{specified_params['base_rtt']}ms RTT-",
    'ecn_threshold': lambda: f"ECN Threshold = {specified_params['ecn_threshold']}ms -",
    'rx0_ecn': lambda: f"ServerA ECN={specified_params['rx0_ecn']}-",
    'rx1_ecn': lambda: f"ServerB ECN={specified_params['rx1_ecn']}-",
    'ecn_fallback': lambda: f"ECN Fallback={specified_params['ecn_fallback']}"
     }
    

    
    desired_order = ['FIFO', 'single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2']
    #desired_order = ['FIFO', 'single_queue_FQ']
    
    # Convert the dictionary to a Pandas DataFrame
    df = pd.DataFrame(plot_heatmap_for_fixed_btl(sorted_throughputs_tx0, sorted_throughputs_tx1))
    df = df.reindex(desired_order)
    df=df.rename(index={'FQ_Codel': 'FQ Codel'})
    df=df.rename(index={'single_queue_FQ': 'Single  \nQueue FQ'})
    df_rtt = pd.DataFrame(plot_heatmap_for_rtt(sorted_rtts_tx0, sorted_rtts_tx1))
    df_rtt = df_rtt.reindex(desired_order)
    df_rtt=df_rtt.rename(index={'FQ_Codel': 'FQ Codel'})
    df_rtt=df_rtt.rename(index={'single_queue_FQ': 'Single  \nQueue FQ'})
    df_masked = np.ma.masked_invalid(df)
    df_masked_rtt = np.ma.masked_invalid(df_rtt)

    
    dynamic_title = ''.join(val() for key, val in title_map.items() if key != factor_y)
    cmap = plt.cm.coolwarm  # Start with the coolwarm colormap
    cmap.set_bad(color='black')  # Set the color for masked values (None/NaN)
    
    #Plot the heatmap
    #plt.figure(figsize=(12, 8))
    
    ax1 = axes1[index % 2, index // 2] 
    #ax1 = axes1[index]
    sns.heatmap(df, annot=True, cmap=cmap, cbar_kws={'label': 'Prague Throughput Share'}, annot_kws={"size": 50}, vmin=0, vmax=1, ax=ax1, cbar=False)
    ax1.set_title(dynamic_title, fontsize=20)
    ax1.set_xlabel('Buffer Size (n x BDP)', fontsize=20)
    ax1.set_ylabel("AQM Types", fontsize=20)
    ax1.set_yticklabels(ax1.get_yticklabels(), fontsize=10) # Adjust for y-axis labels
    ax1.set_xticklabels(ax1.get_xticklabels(), fontsize=20) # Adjust for x-axis labels
    
    ax2 = axes2[index % 2, index // 2] 
    #ax2 = axes2[index] 
    sns.heatmap(df_rtt, annot=True, cmap=cmap, cbar_kws={'label': 'Cubic Relative Queuing Delay'}, annot_kws={"size": 50},  vmin=-1, vmax=1, ax=ax2, cbar=False)
    ax2.set_title(dynamic_title, fontsize=20)
    #ax2.set_xlabel(factor_y, fontsize=40)
    ax2.set_xlabel('Buffer Size (n x BDP)', fontsize=20)
    ax2.set_ylabel("AQM Types", fontsize=20)
    ax2.set_yticklabels(ax2.get_yticklabels(), fontsize=20) # Adjust for y-axis labels
    ax2.set_xticklabels(ax2.get_xticklabels(), fontsize=20) # Adjust for x-axis labels
    
    
plt.figure(fig1.number)
fig1.suptitle('100 Mbps - Server A ECN: AccECN - Server B ECN: Classic ECN - ECN Fallback: OFF', fontsize=45) 
#fig1.subplots_adjust(hspace=0.15)  # Adjust the vertical spacing
cbar_ax = fig1.add_axes([0.92, 0.15, 0.02, 0.7])  # x-position, y-position, width, height
cbar=fig1.colorbar(ax1.collections[0], cax=cbar_ax)
cbar.set_label('Prague Throughput Share', size=40)  
cbar.ax.tick_params(labelsize=35)
plt.tight_layout(rect=[0, 0.01, 0.9, 0.98], pad=1.08, h_pad=1.5, w_pad=1.08)
plt.savefig('/home/fabric/work/throughput.png', dpi=100)



plt.figure(fig2.number)
fig2.suptitle('100 Mbps - Server A ECN: AccECN - Server B ECN: Classic ECN - ECN Fallback: OFF', fontsize=45) 
cbar_ax = fig2.add_axes([0.92, 0.15, 0.02, 0.7])  # x-position, y-position, width, height
cbar=fig2.colorbar(ax2.collections[0], cax=cbar_ax)
cbar.set_label('Cubic Relative Queuing Delay', size=40)  
cbar.ax.tick_params(labelsize=35)
plt.tight_layout(rect=[0, 0.01, 0.9, 0.98], pad=1.08, h_pad=1.5, w_pad=1.08)
plt.savefig('/home/fabric/work/relativedelay.png', dpi=100)
 
```
:::








