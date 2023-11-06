
::: {.cell .markdown}
### Configure Experiment
:::

::: {.cell .code}
```python
# #installing the kernel
# pkg_list = ['iproute2_5.10.0-1_amd64.deb',
#             'iproute2-doc_5.10.0-1_all.deb',
#             'linux-headers-5.15.72-43822a283-prague-43_1_amd64.deb',
#             'linux-image-5.15.72-43822a283-prague-43_1_amd64.deb',
#             'linux-libc-dev_1_amd64.deb']
# for node in slice.get_nodes():
# 	for pkg in pkg_list:
# 	    node.upload_file("/home/fabric/work/debian_build/" + pkg, "/home/ubuntu/" + pkg)
# 	node.execute("sudo dpkg -i " + " ".join(pkg_list) + "; sudo reboot")
for node in slice.get_nodes():
    # Download and unzip the kernel package
    node.execute("wget https://github.com/L4STeam/linux/releases/download/testing-build/l4s-testing.zip")
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


#configuration for DUALPI2 bottleneck
cmd_dualpi2="""sudo apt install -y git gcc make bison flex libdb-dev libelf-dev
sudo git clone https://github.com/L4STeam/iproute2.git && cd iproute2
sudo ./configure
sudo make
sudo make install"""
slice.get_node(name="router").execute(cmd_dualpi2)


```
:::