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

tx0_egress_iface  = tx0_node.get_interface(network_name = "net-tx0")
tx1_egress_iface  = tx1_node.get_interface(network_name = "net-tx1")

delay_ingress_tx0_iface  = delay_node.get_interface(network_name = "net-tx0")
delay_ingress_tx1_iface  = delay_node.get_interface(network_name = "net-tx1")
delay_egress_iface  = delay_node.get_interface(network_name = "net-delay-router")
delay_ingress_tx0_name = delay_ingress_tx0_iface.get_device_name()
delay_ingress_tx1_name = delay_ingress_tx1_iface.get_device_name()
delay_egress_name = delay_egress_iface.get_device_name()

router_ingress_iface  = router_node.get_interface(network_name = "net-delay-router")
router_egress_rx0_iface  = router_node.get_interface(network_name = "net-rx0")
router_egress_rx1_iface  = router_node.get_interface(network_name = "net-rx1")

router_egress_rx0_name  = router_egress_rx0_iface.get_device_name()
router_egress_rx1_name  = router_egress_rx1_iface.get_device_name()


rx0_ingress_iface  = rx0_node.get_interface(network_name = "net-rx0")
rx1_ingress_iface  = rx1_node.get_interface(network_name = "net-rx1")
```
:::

::: {.cell .code}
```python
# generate full factorial experiment
import itertools

exp_factors = { 
    'n_bdp': [0.5, 2, 5, 10], # n x bandwidth delay product
    'btl_capacity': [100, 1000],
    'base_rtt': [10, 50, 100],
    'aqm': ['FIFO', 'single queue FQ', 'Codel', 'FQ', 'FQ_Codel', 'DualPI2'],
    'ecn_threshold': [5, 20],
    'ecn_fallback': [0, 1], # 0: OFF, 1: ON
    'rx0_ecn': [0, 1, 2], #0: noecn, 1:ecn, 2:accecn
    'rx1_ecn': [0, 1, 2]  #0: noecn, 1:ecn, 2:accecn

}

factor_names = [k for k in exp_factors]
factor_lists = list(itertools.product(*exp_factors.values()))

exp_lists = []
for factor_l in factor_lists:
    temp_dict = dict(zip(factor_names, factor_l))
    if temp_dict['aqm'] == 'FIFO':
        del temp_dict['ecn_threshold']
    exp_lists.append(temp_dict)

data_dir = slice_name + 'singlebottleneck'
```
:::

::: {.cell .code}
```python
# run experiments
import time
d = 2 #duration in seconds

em = [delay_ingress_tx0_name, delay_ingress_tx1_name, delay_egress_name]

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
    name_prague="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d.txt" % ("prague",exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])
    name_cubic="%s_%0.1f_%d_%d_%s_%s_%d_%d_%d.txt" % ("cubic",exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])
    
    file_out = data_dir_tx0 + "-"+ name_prague
    stdout, stderr = tx0_node.execute("ls " + file_out, quiet=True) # run this on the node that saves the output file #write 4 lines

    if len(stdout):
        print("Already have " + file_out + ", skipping")

    elif len(stderr):
        print("Running experiment to generate " + file_out) 
        
        # delay at emulator
        for e in em:
            cmds = "sudo tc qdisc replace dev {iface} root netem delay {owd}ms limit 60000".format(iface=e, owd=exp['base_rtt']/2)
            delay_node.execute(cmds)
            print("successfull")
        
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
        if exp['aqm']=='FIFO':
            cmds = '''
            sudo tc qdisc del dev {iface} root
            sudo tc qdisc replace dev {iface} root handle 1: htb default 3 
            sudo tc class add dev {iface} parent 1: classid 1:3 htb rate {capacity}mbit 
            sudo tc qdisc add dev {iface} parent 1:3 handle 3: bfifo limit {buffer} 
            '''.format(iface=router_ingress_name, capacity=exp['btl_capacity'], buffer=btl_limit)
            router_node.execute(cmds)
        
        elif exp['aqm']=='single queue FQ':
            cmds = '''
            sudo tc qdisc del dev {iface} root
            sudo tc qdisc replace dev {iface} root handle 1: htb default 3
            sudo tc class add dev {iface} parent 1: classid 1:3 htb rate {capacity}mbit
            sudo tc qdisc replace dev {iface} parent 1:3 handle 3: fq limit {packet_limit} flow_limit {packet_limit} orphan_mask 0 ce_threshold {threshold}ms
            '''.format(iface=router_egress_name, capacity=exp['btl_capacity'], packet_limit=packet_number, threshold=exp['ecn_threshold'])
            router_node.execute(cmds)
            
            
        elif exp['aqm']=='Codel':
            cmds = '''
            sudo tc qdisc del dev {iface} root
            sudo tc qdisc replace dev {iface} root handle 1: htb default 3
            sudo tc class add dev {iface} parent 1: classid 1:3 htb rate {capacity}mbit
            sudo tc qdisc replace dev {iface} parent 1:3 handle 3: codel limit {packet_limit} target {target}ms interval 100ms ecn ce_threshold {threshold}ms
            '''.format(iface=router_egress_name, capacity=exp['btl_capacity'], packet_limit=packet_number, target=exp['base_rtt']*exp['n_bdp'], threshold=exp['ecn_threshold'])
            router_node.execute(cmds)
            
            
        elif exp['aqm']=='FQ':
            cmds = '''
            sudo tc qdisc del dev {iface} root
            sudo tc qdisc replace dev {iface} root handle 1: htb default 3
            sudo tc class add dev {iface} parent 1: classid 1:3 htb rate {capacity}mbit
            sudo tc qdisc replace dev {iface} parent 1:3 handle 3: fq limit {packet_limit} flow_limit {packet_limit} ce_threshold {threshold}ms
            '''.format(iface=router_egress_name, capacity=exp['btl_capacity'], packet_limit=packet_number, threshold=exp['ecn_threshold'])
            router_node.execute(cmds)
            
            
        elif exp['aqm']=='FQ_Codel':
            cmds = '''
            sudo tc qdisc del dev {iface} root
            sudo tc qdisc replace dev {iface} root handle 1: htb default 3
            sudo tc class add dev {iface} parent 1: classid 1:3 htb rate {capacity}mbit
            sudo tc qdisc replace dev {iface} parent 1:3 handle 3: fq_codel limit {packet_limit} target {target}ms interval 100ms ecn ce_threshold {threshold}ms
            '''.format(iface=router_egress_name, capacity=exp['btl_capacity'], packet_limit=packet_number, target=exp['base_rtt']*exp['n_bdp'], threshold=exp['ecn_threshold'])
            router_node.execute(cmds)
        
        elif exp['aqm']=='DualPI2':
            cmds = '''
            sudo tc qdisc del dev {iface} root
            sudo tc qdisc replace dev {iface} root handle 1: htb default 3
            sudo tc class add dev {iface} parent 1: classid 1:3 htb rate {capacity}mbit
            sudo tc qdisc add dev {iface} parent 1:3 handle 3: dualpi2 target {threshold}ms
            '''.format(iface=router_egress_name, capacity=exp['btl_capacity'], threshold=exp['ecn_threshold'])
            router_node.execute(cmds)
            
    
        #starting experiment
        #name_prague="/%s_%0.1f_%d_%d_%s_%s_%s_%s_%s.txt" % ("prague",exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])
        #name_cubic="/%s_%0.1f_%d_%d_%s_%s_%s_%s_%s.txt" % ("cubic",exp['n_bdp'], exp['btl_capacity'], exp['base_rtt'], exp['aqm'], str(exp.get('ecn_threshold', 'none')), exp['ecn_fallback'], exp['rx0_ecn'], exp['rx1_ecn'])

        rx0_node.execute("killall iperf3")
        rx1_node.execute("killall iperf3")
        
        ss_tx0_script="rm -f {flow}-ss.txt; start_time=$(date +%s); while true; do ss --no-header -eipn dst 10.0.3.100 | ts '%.s' | tee -a {flow}-ss.txt; current_time=$(date +%s); elapsed_time=$((current_time - start_time));  if [ $elapsed_time -ge {duration} ]; then break; fi; sleep 0.1; done;"
        ss_tx1_script="rm -f {flow}-ss.txt; start_time=$(date +%s); while true; do ss --no-header -eipn dst 10.0.4.100 | ts '%.s' | tee -a {flow}-ss.txt; current_time=$(date +%s); elapsed_time=$((current_time - start_time));  if [ $elapsed_time -ge {duration} ]; then break; fi; sleep 0.1; done;"

        #print("Starting experiment with {1} bdp {2} capacity {3} rtt {4} {5} thrshold {6} ecn_fallback {7} rx0 {8} rx1 for {duration} seconds".format(duration=d, 1=exp['n_bdp'], 2=exp['btl_capacity'], 3=exp['base_rtt'], 4=exp['aqm'], 5=exp['ecn_threshold'], 6= exp['ecn_fallback'], 7=exp['rx0_ecn'], 8=exp['rx1_ecn']))
        
        rx0_node.execute("iperf3 -s -1 -p 4000 -D")
        rx1_node.execute("iperf3 -s -1 -p 5000 -D")
        
        tx0_node.execute_thread(ss_tx0_script.format(flow=name_prague, duration=d))
        tx1_node.execute_thread(ss_tx1_script.format(flow=name_cubic, duration=d))
        
        tx0_node.execute_thread("sleep 1; iperf3 -c 10.0.3.100 -t {duration} -P {flows} -C prague -p 4000 -J > {flow}-result.json".format(flow =name_prague, duration=d, flows=1))
        stdout, stderr = tx1_node.execute("sleep 1; iperf3 -c 10.0.4.100 -t {duration} -P {flows} -C cubic -p 5000 -J > {flow}-result.json".format(flow =name_cubic, duration=d, flows=1))
        time.sleep(3)
        
        break
        
tx0_node.execute('rm -r '+data_dir_tx0)
tx0_node.execute('mkdir '+data_dir_tx0)

tx0_node.execute('mv *.json '+ data_dir_tx0)
tx0_node.execute('mv *.txt '+ data_dir_tx0)
        
tx0_node.execute('tar -czvf '+data_dir_tx0+ '.tgz ' +  data_dir_tx0)
tx0_node.download_file(data_dir_tx0+'.tgz ', '/home/ubuntu/' + data_dir_tx0+ '.tgz')

tx1_node.execute('rm -r '+data_dir_tx1)
tx1_node.execute('mkdir '+data_dir_tx1)

tx1_node.execute('mv *.json '+ data_dir_tx1)
tx1_node.execute('mv *.txt '+ data_dir_tx1)
        
tx1_node.execute('tar -czvf '+data_dir_tx1+ '.tgz ' +  data_dir_tx1)
tx1_node.download_file(data_dir_tx1+'.tgz ', '/home/ubuntu/' + data_dir_tx1+ '.tgz')
```
:::

