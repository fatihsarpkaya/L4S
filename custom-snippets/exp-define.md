
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
 {'name': "switch", 'cores': 4, 'ram': 32, 'disk': 20, 'image': 'default_ubuntu_22', 'packages': ['iperf3', 'net-tools', 'moreutils']}, 
 {'name': "rx0",    'cores': 4, 'ram': 32, 'disk': 20, 'image': 'default_ubuntu_22', 'packages': ['iperf3', 'net-tools', 'moreutils']}, 
 {'name': "rx1",    'cores': 4, 'ram': 32, 'disk': 20, 'image': 'default_ubuntu_22', 'packages': ['iperf3', 'net-tools', 'moreutils']}
]
net_conf = [
 {"name": "net-tx0", "subnet": "10.0.0.0/24", "nodes": [{"name": "tx0",   "addr": "10.0.0.100"}, {"name": "delay", "addr": "10.0.0.101"}]},
 {"name": "net-tx1", "subnet": "10.0.1.0/24", "nodes": [{"name": "tx1", "addr": "10.0.1.100"}, {"name": "delay", "addr": "10.0.1.101"}]},
 {"name": "net-delay-router", "subnet": "10.0.2.0/24", "nodes": [{"name": "delay",   "addr": "10.0.2.1"}, {"name": "router", "addr": "10.0.2.2"}]},
 {"name": "net-router-switch", "subnet": "10.0.5.0/24", "nodes": [{"name": "router",   "addr": "10.0.5.1"}, {"name": "switch", "addr": "10.0.5.2"}]},
 {"name": "net-rx0", "subnet": "10.0.3.0/24", "nodes": [{"name": "rx0",   "addr": "10.0.3.100"}, {"name": "switch", "addr": "10.0.3.101"}]},
 {"name": "net-rx1", "subnet": "10.0.4.0/24", "nodes": [{"name": "rx1", "addr": "10.0.4.100"}, {"name": "switch", "addr": "10.0.4.101"}]}

]
route_conf = [
 {"addr": "10.0.3.0/24", "gw": "10.0.0.101", "nodes": ["tx0"]}, 
 {"addr": "10.0.4.0/24", "gw": "10.0.1.101", "nodes": ["tx1"]}, 
 {"addr": "10.0.3.0/24", "gw": "10.0.2.2", "nodes": ["delay"]},
 {"addr": "10.0.4.0/24", "gw": "10.0.2.2", "nodes": ["delay"]},
 {"addr": "10.0.3.0/24", "gw": "10.0.5.2", "nodes": ["router"]},
 {"addr": "10.0.4.0/24", "gw": "10.0.5.2", "nodes": ["router"]},

 {"addr": "10.0.0.0/24", "gw": "10.0.3.101", "nodes": ["rx0"]},
 {"addr": "10.0.1.0/24", "gw": "10.0.4.101", "nodes": ["rx1"]},
 {"addr": "10.0.0.0/24", "gw": "10.0.5.1", "nodes": ["switch"]},
 {"addr": "10.0.1.0/24", "gw": "10.0.5.1", "nodes": ["switch"]},
 {"addr": "10.0.0.0/24", "gw": "10.0.2.1", "nodes": ["router"]},
 {"addr": "10.0.1.0/24", "gw": "10.0.2.1", "nodes": ["router"]},

]
exp_conf = {'cores': sum([ n['cores'] for n in node_conf]), 'nic': sum([len(n['nodes']) for n in net_conf]) }
```
:::
