::: {.cell .markdown}
### Execute Experiment
:::

::: {.cell .code}
```python
# nodes and instances

tx0_node = slice.get_node(name="tx0")
tx1_node = slice.get_node(name="tx1")
rx0_node = slice.get_node(name="rx0")
rx1_node = slice.get_node(name="rx1")
delay_node = slice.get_node(name="delay")
router_node = slice.get_node(name="router")
# interfaces

tx0_egress_iface  = tx0_node.get_interface(network_name = "net-tx")
tx1_egress_iface  = tx1_node.get_interface(network_name = "net-tx")

delay_ingress_tx_iface  = delay_node.get_interface(network_name = "net-tx")
delay_egress_iface  = delay_node.get_interface(network_name = "net-delay-router")
delay_ingress_tx_name = delay_ingress_tx_iface.get_device_name()
delay_egress_name = delay_egress_iface.get_device_name()

router_ingress_iface  = router_node.get_interface(network_name = "net-delay-router")
router_egress_iface  = router_node.get_interface(network_name = "net-rx")
router_egress_name  = router_egress_iface.get_device_name()


rx0_ingress_iface  = rx0_node.get_interface(network_name = "net-rx")
rx1_ingress_iface  = rx1_node.get_interface(network_name = "net-rx")
```
:::

::: {.cell .code}
```python
# generate full factorial experiment
import itertools

exp_factors = {
    'n_bdp': [0.5, 2, 5, 10],  # n x bandwidth delay product
    'btl_capacity': [100, 1000],
    'base_rtt': [5, 10, 50, 100],
    'aqm': ['FIFO', 'single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2'],
    #'aqm': ['single_queue_FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2'],
    'ecn_threshold': [1, 5, 20],
    'ecn_fallback': [0, 1],  #fallback algorithm, it falls back when it detects single queue classic ECN bottleneck # 0: OFF, 1: ON
    'rx0_ecn': [0, 1, 2],  # 0: noecn, 1: ecn, 2: accecn
    'rx1_ecn': [0, 1],  # 0: noecn, 1: ecn
    'cc_tx0': ["prague"],
    'cc_tx1': ["cubic"],
    'trial': [1, 2, 3, 4, 5]
}

factor_names = [k for k in exp_factors]
factor_lists = list(itertools.product(*exp_factors.values()))

exp_lists = []

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

data_dir_tx0 = slice_name + 'singlebottleneck'+"-tx0"
data_dir_tx1 = slice_name + 'singlebottleneck'+"-tx1"

print("Number of experiments:",len(exp_lists))
```
:::

::: {.cell .code}
```python
# run experiments
import time
d = 60 #duration in seconds

em = [delay_ingress_tx_name, delay_egress_name]

commands_noecn='''
sudo sysctl -w net.ipv4.tcp_congestion_control=cubic  
sudo sysctl -w net.ipv4.tcp_ecn=0''' #tcp_prague, no ECN

commands_ecn='''
sudo sysctl -w net.ipv4.tcp_congestion_control=cubic  
sudo sysctl -w net.ipv4.tcp_ecn=1''' #tcp_prague, ECN

commands_accecn='''
sudo sysctl -w net.ipv4.tcp_congestion_control=prague  
sudo sysctl -w net.ipv4.tcp_ecn=3''' #tcp_prague, AccECN

server_ecn_list=[commands_noecn, commands_ecn, commands_accecn]

for exp in exp_lists:

    # check if we already ran this experiment
    # (allow stop/resume)
    name_tx0="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (exp['cc_tx0'],exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])
    name_tx1="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d" % (exp['cc_tx1'],exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])
    
    file_out_tx0_json = name_tx0+"-result.json"
    file_out_tx0_ss = name_tx0+"-ss.txt"
    stdout_tx0_json, stderr_tx0_json = tx0_node.execute("ls " + file_out_tx0_json, quiet=True) 
    stdout_tx0_ss, stderr_tx0_ss = tx0_node.execute("ls " + file_out_tx0_ss, quiet=True)
    
    file_out_tx1_json =name_tx1+"-result.json"
    file_out_tx1_ss = name_tx1+"-ss.txt"
    stdout_tx1_json, stderr_tx1_json = tx1_node.execute("ls " + file_out_tx1_json, quiet=True) 
    stdout_tx1_ss, stderr_tx1_ss = tx1_node.execute("ls " + file_out_tx1_ss, quiet=True) 

    if len(stdout_tx0_json) and len(stdout_tx0_ss) and len(stdout_tx1_json) and len(stdout_tx1_ss):
        print("Already have " + name_tx0 + " and "+ name_tx1 + ", skipping")

    elif len(stderr_tx0_json) or len(stderr_tx0_ss) or len(stderr_tx1_json) or len(stderr_tx1_ss):
        print("Running experiment to generate " + name_tx0 + " and "+ name_tx1) 
        
        # delay at emulator
        for e in em:
            cmds = "sudo tc qdisc replace dev {iface} root netem delay {owd}ms limit 60000".format(iface=e, owd=exp['base_rtt']/2)
            delay_node.execute(cmds)
        
        # fixed values
        btl_limit    = int(1000*exp['n_bdp']*exp['btl_capacity']*2*exp['base_rtt']/8) # limit of the bottleneck, n_bdp x BDP in bytes 
        packet_number=int(btl_limit/1500)+1
        
        
        #ecn-fallback configuration
               
        commands = "cd /sys/module/tcp_prague/parameters && echo {value} | sudo tee prague_ecn_fallback".format(value=str(exp['ecn_fallback']))
        tx0_node.execute(commands)
        
        #receiver ecn configuration
        rx0_node.execute(server_ecn_list[exp['rx0_ecn']])
        rx1_node.execute(server_ecn_list[exp['rx1_ecn']])
        
        #aqm type selection
        cmd_prefix = '''
            sudo tc qdisc del dev {iface} root
            sudo tc qdisc replace dev {iface} root handle 1: htb default 3 
            sudo tc class add dev {iface} parent 1: classid 1:3 htb rate {capacity}mbit 
            '''.format(iface=router_egress_name, capacity=exp['btl_capacity'], buffer=btl_limit)
        cmds_specific = {
		'FIFO': "sudo tc qdisc add dev {iface} parent 1:3 handle 3: bfifo limit {buffer}".format(iface=router_egress_name, capacity=exp['btl_capacity'], buffer=btl_limit),
		'single_queue_FQ': "sudo tc qdisc replace dev {iface} parent 1:3 handle 3: fq limit {packet_limit} flow_limit {packet_limit} orphan_mask 0 ce_threshold {threshold}ms".format(iface=router_egress_name, capacity=exp['btl_capacity'], packet_limit=packet_number, threshold=exp['ecn_threshold']),
		'Codel': "sudo tc qdisc replace dev {iface} parent 1:3 handle 3: codel limit {packet_limit} target {target}ms interval 100ms ecn ce_threshold {threshold}ms".format(iface=router_egress_name, capacity=exp['btl_capacity'], packet_limit=packet_number, target=exp['base_rtt']*exp['n_bdp'], threshold=exp['ecn_threshold']),
		'FQ': "sudo tc qdisc replace dev {iface} parent 1:3 handle 3: fq limit {packet_limit} flow_limit {packet_limit} ce_threshold {threshold}ms".format(iface=router_egress_name, capacity=exp['btl_capacity'], packet_limit=packet_number, threshold=exp['ecn_threshold']),
		'FQ_Codel': "sudo tc qdisc replace dev {iface} parent 1:3 handle 3: fq_codel limit {packet_limit} target {target}ms interval 100ms ecn ce_threshold {threshold}ms".format(iface=router_egress_name, capacity=exp['btl_capacity'], packet_limit=packet_number, target=exp['base_rtt']*exp['n_bdp'], threshold=exp['ecn_threshold']),
		'DualPI2': "sudo tc qdisc add dev {iface} parent 1:3 handle 3: dualpi2 target {threshold}ms".format(iface=router_egress_name, capacity=exp['btl_capacity'], threshold=exp['ecn_threshold'])
        }
        router_node.execute(cmds_prefix)
        router_node.execute(cmds_specific[ exp['aqm'] ])
            
        rx0_node.execute("killall iperf3")
        rx1_node.execute("killall iperf3")
        
        ss_tx0_script="rm -f {flow}-ss.txt; start_time=$(date +%s); while true; do ss --no-header -eipn dst 10.0.3.100 | ts '%.s' | tee -a {flow}-ss.txt; current_time=$(date +%s); elapsed_time=$((current_time - start_time));  if [ $elapsed_time -ge {duration} ]; then break; fi; sleep 0.1; done;"
        ss_tx1_script="rm -f {flow}-ss.txt; start_time=$(date +%s); while true; do ss --no-header -eipn dst 10.0.4.100 | ts '%.s' | tee -a {flow}-ss.txt; current_time=$(date +%s); elapsed_time=$((current_time - start_time));  if [ $elapsed_time -ge {duration} ]; then break; fi; sleep 0.1; done;"

        #print("Starting experiment with {1} bdp {2} capacity {3} rtt {4} {5} thrshold {6} ecn_fallback {7} rx0 {8} rx1 for {duration} seconds".format(duration=d, 1=exp['n_bdp'], 2=exp['btl_capacity'], 3=exp['base_rtt'], 4=exp['aqm'], 5=exp['ecn_threshold'], 6= exp['ecn_fallback'], 7=exp['rx0_ecn'], 8=exp['rx1_ecn']))
        
        rx0_node.execute("iperf3 -s -1 -p 4000 -D")
        rx1_node.execute("iperf3 -s -1 -p 5000 -D")
        
        tx0_node.execute_thread(ss_tx0_script.format(flow=name_tx0, duration=d))
        tx1_node.execute_thread(ss_tx1_script.format(flow=name_tx1, duration=d))
        
        tx0_node.execute_thread("sleep 1; iperf3 -c 10.0.5.100 -t {duration} -P {flows} -C {cc} -p 4000 -J > {flow}-result.json".format(flow =name_tx0, duration=d, flows=1, cc=exp['cc_tx0']))
        stdout, stderr = tx1_node.execute("sleep 1; iperf3 -c 10.0.5.101 -t {duration} -P {flows} -C {cc} -p 5000 -J > {flow}-result.json".format(flow =name_tx1, duration=d, flows=1, cc=exp['cc_tx1']))
        time.sleep(3)  # time.sleep(1)
        
print("finished")
        
        
```
:::


