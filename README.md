# L4S

Low Latency, Low Loss, Scalable Throughput (L4S) seeks to reduce network latency by introducing new protocols for congestion control and queue management at hosts, servers, and routers throughout the Internet. However, because it requires such widespread changes, it is critical to understand the practical implications of deploying this technology incrementally in diverse network environments. 

In this experiment, we will see how two types of TCP congestion control mechanisms — TCP Prague (a scalable approach) and TCP Cubic/BBRv1/BBRv2 (a traditional approach) — interact and affect performance when they meet at the same network bottleneck. This study methodically examines partial L4S deployments under an array of conditions, considering various Active Queue Management (AQM) types, network latencies (RTT), Explicit Congestion Notification (ECN) configurations and bottleneck bandwidth scenarios.

To run this experiment on [FABRIC](https://fabric-testbed.net), you should have a FABRIC account with keys configured, and be part of a FABRIC project. You will need to have set up SSH keys and understand how to use the Jupyter interface in FABRIC.

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
