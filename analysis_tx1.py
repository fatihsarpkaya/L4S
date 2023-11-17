# generate full factorial experiment
import itertools
import json
import pandas as pd

exp_factors = {
    'n_bdp': [0.5, 2, 5, 10],  # n x bandwidth delay product
    'btl_capacity': [100],
    'base_rtt': [5, 10, 50, 100],
    'aqm': ['DualPI2'],#'aqm': ['FIFO', 'single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2'],
    'ecn_threshold': [1, 5, 20],
    'ecn_fallback': [0, 1],  #fallback algorithm, it falls back when it detects single queue classic ECN bottleneck # 0: OFF, 1: ON
    'rx0_ecn': [0, 1, 2],  # 0: noecn, 1: ecn, 2: accecn
    'rx1_ecn': [0, 1],  # 0: noecn, 1: ecn
    'cc_tx0': ["prague"],
    'cc_tx1': ["cubic"],
    'trial': [1] #'trial': [1, 2, 3, 4, 5]
}

factor_names = [k for k in exp_factors]
factor_lists = list(itertools.product(*exp_factors.values()))

exp_lists = []
slice_name="l4s-1-ashusri_0000051121"

seen_combinations = set()

for factor_l in factor_lists:
    temp_dict = dict(zip(factor_names, factor_l))
    if temp_dict['n_bdp'] * temp_dict['base_rtt'] >= temp_dict['ecn_threshold']:
        if temp_dict['aqm'] == 'FIFO':
            del temp_dict['ecn_threshold']
        # Convert dict to a frozenset for set operations
        fs = frozenset(temp_dict.items())
    
        if fs not in seen_combinations:
            seen_combinations.add(fs)
            exp_lists.append(temp_dict)

data_dir_tx1 = slice_name + 'singlebottleneck'+"-tx1"

print("Number of experiments:",len(exp_lists))

#get all throughput and SRTT data

throughput_data = {}  # Initialize the dictionary

srtt_data = {}

for exp in exp_lists:


    name_tx1="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d_%d" % (exp['cc_tx1'],exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'], exp['trial'])

    # Load the JSON output file into a Python object
    ##### Average Throughput for Each Flow ****

    with open("/home/ubuntu/"+data_dir_tx1+"/"+"{name_tx1}-result.json".format(name_tx1=name_tx1)) as f:
        iperf3_data = json.load(f)

    throughput_data[name_tx1]  = iperf3_data['end']['sum_received']['bits_per_second']/(1000000*1) # to convert Mbit

    ##### Average SRTT for Each Flow ******

    columns = ['timestamp', 'flow ID', 'cwnd', 'srtt']
    df_f1= pd.read_csv("/home/ubuntu/"+data_dir_tx1+"/"+"{name_tx1}-ss.csv".format(name_tx1=name_tx1), names=columns)

    # Filter out rows with flow ID = 4, they are for the control flows
    df_f1= df_f1[df_f1['flow ID'] != 4]

    average_RTT_f1 = df_f1['srtt'].mean()

    srtt_data[name_tx1] = average_RTT_f1


# Save throughput_data to a JSON file
with open('throughput_data.json', 'w') as f:
    json.dump(throughput_data, f)

# Save srtt_data to a JSON file
with open('srtt_data.json', 'w') as f:
    json.dump(srtt_data, f)