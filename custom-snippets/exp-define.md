::: {.cell .markdown}
### Define configuration for this experiment (example)
:::

::: {.cell .code}
```python
slice_name="l4s-" + fablib.get_bastion_username()

node_conf = [
 {'name': "tx0",    'cores': 2, 'ram': 4, 'disk': 10, 'image': 'default_ubuntu_22', 'packages': ['iperf3']}, 
 {'name': "tx1",    'cores': 2, 'ram': 4, 'disk': 10, 'image': 'default_ubuntu_22', 'packages': ['iperf3']}, 
 {'name': "router", 'cores': 2, 'ram': 4, 'disk': 10, 'image': 'default_ubuntu_22', 'packages': []}, 
 {'name': "delay", 'cores': 2, 'ram': 4, 'disk': 10, 'image': 'default_ubuntu_22', 'packages': []}, 
 {'name': "rx0",    'cores': 2, 'ram': 4, 'disk': 10, 'image': 'default_ubuntu_22', 'packages': ['iperf3']}, 
 {'name': "rx1",    'cores': 2, 'ram': 4, 'disk': 10, 'image': 'default_ubuntu_22', 'packages': ['iperf3']}
]
net_conf = [
 {"name": "net-tx", "subnet": "10.0.0.0/24", "nodes": [{"name": "tx0",   "addr": "10.0.0.100"}, {"name": "tx1", "addr": "10.0.0.101"}, {"name": "delay", "addr": "10.0.0.1"}]},
  {"name": "net-mid", "subnet": "10.0.1.0/24", "nodes": [{"name": "delay",   "addr": "10.0.1.2"}, {"name": "router", "addr": "10.0.1.1"}]},
 {"name": "net-tx", "subnet": "10.0.0.0/24", "nodes": [{"name": "rx0",   "addr": "10.0.2.100"}, {"name": "rx1", "addr": "10.0.2.101"}, {"name": "router", "addr": "10.0.2.1"}]}
]
route_conf = [
 {"addr": "10.0.2.0/24", "gw": "10.0.0.1", "nodes": ["tx0", "tx1"]}, 
 {"addr": "10.0.0.0/24", "gw": "10.0.2.1", "nodes": ["rx0", "rx1"]}
]
exp_conf = {'cores': sum([ n['cores'] for n in node_conf]), 'nic': sum([len(n['nodes']) for n in net_conf]) }
```
:::
