
::: {.cell .markdown}
### Configure Experiment
:::

::: {.cell .code}
```python
for node in slice.get_nodes():
    # Download and unzip the kernel package
    node.execute("wget https://github.com/L4STeam/linux/releases/download/testing-build/l4s-testing.zip")
    node.execute("sudo apt install unzip")
    node.execute("unzip l4s-testing.zip")
    
    # Install the kernel packages and update GRUB
    node.execute("sudo dpkg --install debian_build/*")
    node.execute("sudo update-grub")
    node.execute("sudo reboot")

# wait for all nodes to come back up
slice.wait_ssh(progress=True)
for node in slice.get_nodes():
    # check kernel version
    node.execute("hostname; uname -a")
```
:::

::: {.cell .code}
```python
#inital configuration for the senders
slice.get_node(name="tx0").execute("sudo modprobe tcp_prague")
slice.get_node(name="tx0").execute("sudo sysctl -w net.ipv4.tcp_congestion_control=prague")
slice.get_node(name="tx0").execute("sudo sysctl -w net.ipv4.tcp_ecn=3")

slice.get_node(name="tx1").execute("sudo sysctl -w net.ipv4.tcp_congestion_control=cubic")
slice.get_node(name="tx1").execute("sudo sysctl -w net.ipv4.tcp_ecn=1")
```
:::

::: {.cell .code}
```python
#configuration for DUALPI2 bottleneck
cmd_dualpi2="""sudo apt-get update
sudo apt -y install git gcc make bison flex libdb-dev libelf-dev pkg-config libbpf-dev libmnl-dev libcap-dev libatm1-dev selinux-utils libselinux1-dev
sudo git clone https://github.com/L4STeam/iproute2.git && cd iproute2
sudo ./configure
sudo make
sudo make install"""
slice.get_node(name="router").execute(cmd_dualpi2)
slice.get_node(name="router").execute("sudo modprobe sch_dualpi2")
```
:::