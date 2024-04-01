import glob
import itertools
import json
import pandas as pd

import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Assuming the files in the current directory follow a pattern like '*-result.json'
# Adjust the pattern as necessary to match your file naming convention
result_files_pattern = '*-result.json'
throughput_data = {}  # Initialize the dictionary
srtt_data = {}

for result_file in glob.glob(result_files_pattern):
    # Extract the base name (without '-result.json') to use in other file references
    base_name = result_file.replace('-result.json', '')

    # Load the JSON output file into a Python object
    with open(result_file) as f:
        iperf3_data = json.load(f)

    throughput_data[base_name] = iperf3_data['end']['sum_received']['bits_per_second'] / (1000000 * 1)  # to convert Mbit
    srtt_data[base_name] = iperf3_data['end']['streams'][0]['sender']["mean_rtt"] / (1000 * 1)  # to convert ms
    
# # Save throughput_data to a JSON file
with open('throughput_data.json', 'w') as f:
     json.dump(throughput_data, f)
     
# # Save srtt_data to a JSON file
with open('srtt_data.json', 'w') as f:
    json.dump(srtt_data, f)