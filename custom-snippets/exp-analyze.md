
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
import tarfile
# extract tar files 
with tarfile.open(data_dir_tx0+'.tgz ', 'r:gz') as tar:
    tar.extractall()
    
with tarfile.open(data_dir_tx1+'.tgz ', 'r:gz') as tar:
    tar.extractall()
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










