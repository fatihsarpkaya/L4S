
::: {.cell .markdown}
### Define configuration for this experiment
:::

::: {.cell .code}
```python
slice_name="l4s-" + fablib.get_bastion_username()

node_conf = [
 {'name': "tx0",    'cores': 4, 'ram': 32, 'disk': 20, 'image': 'default_ubuntu_22', 'packages': ['iperf3', 'net-tools', 'moreutils']}, 
 {'name': "tx1",    'cores': 4, 'ram': 32, 'disk': 20, 'image': 'default_ubuntu_22', 'packages': ['iperf3', 'net-tools', 'moreutils']}, 
 {'name': "router", 'cores': 4, 'ram': 32, 'disk': 20, 'image': 'default_ubuntu_22', 'packages': ['iperf3', 'net-tools', 'moreutils']}, 
 {'name': "delay", 'cores': 4, 'ram': 32, 'disk': 20, 'image': 'default_ubuntu_22', 'packages': ['iperf3', 'net-tools', 'moreutils']}, 
 {'name': "rx0",    'cores': 4, 'ram': 32, 'disk': 20, 'image': 'default_ubuntu_22', 'packages': ['iperf3', 'net-tools', 'moreutils']}, 
 {'name': "rx1",    'cores': 4, 'ram': 32, 'disk': 20, 'image': 'default_ubuntu_22', 'packages': ['iperf3', 'net-tools', 'moreutils']}
]
net_conf = [
 {"name": "net-tx", "subnet": "10.0.0.0/24", "nodes": [{"name": "tx0",   "addr": "10.0.0.100"}, {"name": "tx1",   "addr": "10.0.0.101"}, {"name": "delay", "addr": "10.0.0.2"}]},
 {"name": "net-delay-router", "subnet": "10.0.2.0/24", "nodes": [{"name": "delay",   "addr": "10.0.2.2"}, {"name": "router", "addr": "10.0.2.1"}]},
 {"name": "net-rx", "subnet": "10.0.5.0/24", "nodes": [{"name": "router",   "addr": "10.0.5.1"}, {"name": "rx0", "addr": "10.0.5.100"}, {"name": "rx1", "addr": "10.0.5.101"}]}

]
route_conf = [
 {"addr": "10.0.5.0/24", "gw": "10.0.0.2", "nodes": ["tx0", "tx1"]}, 
 {"addr": "10.0.5.0/24", "gw": "10.0.2.1", "nodes": ["delay"]},

 {"addr": "10.0.0.0/24", "gw": "10.0.5.1", "nodes": ["rx0", "rx1"]},
 {"addr": "10.0.0.0/24", "gw": "10.0.2.2", "nodes": ["router"]}

]
exp_conf = {'cores': sum([ n['cores'] for n in node_conf]), 'nic': sum([len(n['nodes']) for n in net_conf]) }
```
:::

