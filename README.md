This repository contains the artifacts for the paper [To switch or not to switch to TCP Prague? Incentives for adoption in a partial L4S deployment](https://doi.org/10.1145/3673422.3674896), accepted for presentation at the ANRW '24 workshop.

# L4S

Low Latency, Low Loss, Scalable Throughput (L4S) seeks to reduce network latency by introducing new protocols for congestion control and queue management at hosts, servers, and routers throughout the Internet. However, because it requires such widespread changes, it is critical to understand the practical implications of deploying this technology incrementally in diverse network environments. 

In this experiment, we will see how two types of TCP congestion control mechanisms — TCP Prague (a scalable approach) and TCP Cubic/BBRv1/BBRv2 (a traditional approach) — interact and affect performance when they meet at the same network bottleneck. This study methodically examines partial L4S deployments under an array of conditions, considering various Active Queue Management (AQM) types, network latencies (RTT), Explicit Congestion Notification (ECN) configurations and bottleneck bandwidth scenarios.

To run this experiment on [FABRIC](https://fabric-testbed.net), you should have a FABRIC account with keys configured, and be part of a FABRIC project. You will need to have set up SSH keys and understand how to use the Jupyter interface in FABRIC.

## Important Note on DualPI2 Configuration in the Results

In the paper, the size of the DualPI2 queue is configured with the default parameter of 10,000 packets (approximately 12 BDP in our settings), even though the heatmaps show different buffer sizes on the x-axis. Since the ECN threshold is set to 5 ms in the classic queue and 1 ms in the low-latency queue — and non-ECN packets are dropped — adjusting the queue size for lower BDP values does not significantly affect the results for CUBIC and BBRv1.

## Important Note on BBRv2 ECN Implementation

In our implementation, we identified that the BBRv2 receiver applies classic ECN marking instead of the DCTCP-style marking that BBRv2 expects. A more detailed analysis of this difference is provided in our another paper: [To adopt or not to adopt L4S-compatible congestion control? Understanding performance in a partial L4S deployment](https://doi.org/10.48550/arXiv.2411.10952).

## Reproducing the figures using our experiment data

You can use our experiment data directly to generate the figures in our paper: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1A_0-mLgEVr4zma1-VdYhWUUVzcR6hYfk?usp=sharing)

## Run my Experiment

To reproduce our experiments on FABRIC, log in to the FABRIC testbed's JupyterHub environment. Open a new terminal from the launcher, and run:

> git clone https://github.com/fatihsarpkaya/L4S.git

In order to get the results for Prague throughput and Prague queueing delay heatmaps, run the `single_bottleneck.ipynb` notebook. 

In this notebook, the experiment parameters are chosen as following.
```
 exp_factors = {
    'n_bdp': [0.5, 1, 2, 4, 8],  # n x bandwidth delay product
    'btl_capacity': [100], #in Mbps 
    'base_rtt': [10], # in ms 
    'aqm': ['FIFO', 'single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2'],
    'ecn_threshold': [5], # in ms 
    'ecn_fallback': [0],  #fallback algorithm, TCP Prague falls back to classic TCP when it detects single queue classic ECN bottleneck # 0: OFF, 1: ON  
    'rx_L4S_ecn': [3],  # 0: noecn, 1: ecn, 3: accecn 
    'rx_legacy_ecn': [0],  # 0: noecn, 1: ecn 
    'cc_tx_L4S': ["prague"],
    'cc_tx_legacy': ["cubic"],
    'trial': [1,2,3,4,5,6,7,8,9,10]
}
```

The original results were obtained from 10 trials per experiment, with each experiment lasting 60 seconds. To save time, you may consider reducing the experiment duration. While this shorter duration might not be sufficient for accurate measurements, it should provide a general idea about the throughput and queueing delay.

As mentioned before, the paramaters and the experiment duration could be changed as needed.

Upon completion of the notebook execution, the plots will be saved and displayed at the end of the notebook.

## How FABRIC Enables This Research

Managing a full-factorial experiment design poses challenges, as it requires running a large number of unique experiments due to the different combinations of network settings. 

Key challenges include:
- Not being able to run all experiments at once in a single Jupyter session.
- The need to run different experiments on different slices in parallel.
- The necessity of organizing and tracking all experiment results.

FABRIC's Jupyter notebook interface, combined with its Python library and some of our own tricks, makes it much easier to manage and streamline this process. In this section, we will highlight a few of these methods.

### Generate list of full factorial experiments in notebook 

```
 exp_factors = {
    'n_bdp': [0.5, 1, 2, 4, 8],  # n x bandwidth delay product
    'btl_capacity': [100], #in Mbps 
    'base_rtt': [10], # in ms 
    'aqm': ['FIFO', 'single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2'],
    'ecn_threshold': [5], # in ms 
    'ecn_fallback': [0],  #fallback algorithm, TCP Prague falls back to classic TCP when it detects single queue classic ECN bottleneck # 0: OFF, 1: ON  
    'rx_L4S_ecn': [3],  # 0: noecn, 1: ecn, 3: accecn 
    'rx_legacy_ecn': [0],  # 0: noecn, 1: ecn 
    'cc_tx_L4S': ["prague"],
    'cc_tx_legacy': ["cubic"],
    'trial': [1,2,3,4,5,6,7,8,9,10]
}

flow_number_tx_L4S=1 #number of tx_L4S flows
flow_number_tx_legacy=1 #number of tx_legacy flows

factor_names = [k for k in exp_factors]
factor_lists = list(itertools.product(*exp_factors.values()))

exp_lists = []

seen_combinations = set()

# Removing ECN factor from FIFO bottleneck because it does not support ECN
# Removing the cases where ECN Threshold is less than or equal to the buffer size in time, these cases are not meaningful in practice

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
```

In our notebook (as shown above), we first set up the environment and generate the complete list of experiments before executing any. Each experiment is represented as a dictionary containing all the factor values, and we iterate through this list systematically. When running each experiment with the given factors, we ensure that all the factor values are included in the output file names for easy identification and organization. 

### Allow stop/resume experiments in Jupyter

It is also crucial to be able to stop and resume experiments, as they won’t be able to run within a single Jupyter session. The Jupyter Hub server doesn’t stay active for extended periods, and while FABRIC supports long-term access with tokens, the Jupyter server itself may not survive for that long. Additionally, your FABRIC access token also expires after a certain time.

```
for exp in exp_lists:

    # check if we already ran this experiment
    # (allow stop/resume)
    name_tx_L4S="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d_%d" % (exp['cc_tx_L4S'],exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx_L4S_ecn'], exp['rx_legacy_ecn'], exp['trial'])
    name_tx_legacy="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d_%d" % (exp['cc_tx_legacy'],exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx_L4S_ecn'], exp['rx_legacy_ecn'], exp['trial'])
    
    file_out_tx_L4S_json = name_tx_L4S+"-result.json"
    stdout_tx_L4S_json, stderr_tx_L4S_json = tx_L4S_node.execute("ls " + file_out_tx_L4S_json, quiet=True) 
    
    file_out_tx_legacy_json =name_tx_legacy+"-result.json"
    stdout_tx_legacy_json, stderr_tx_legacy_json = tx_legacy_node.execute("ls " + file_out_tx_legacy_json, quiet=True) 
    

    if len(stdout_tx_L4S_json) and len(stdout_tx_legacy_json):
        print("Already have " + name_tx_L4S + " and "+ name_tx_legacy + ", skipping")

    elif len(stderr_tx_L4S_json) or len(stderr_tx_legacy_json):
        print("Running experiment to generate " + name_tx_L4S + " and "+ name_tx_legacy)
```

To address this, we designed our loop to allow starting, stopping, and resuming experiments (as shown above). If needed, we can even add additional factors later on. The system checks if the experiment results already exist and skips those experiments, making it much easier to manage a large number of experiments by enabling us to pause and resume as necessary.

