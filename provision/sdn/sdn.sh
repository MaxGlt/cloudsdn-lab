#!/bin/bash

# Update and upgrade the system
sudo apt-get update -y && sudo apt-get upgrade -y

# Install Open vSwitch
sudo apt-get install -y openvswitch-switch

# Enable and start the Open vSwitch service
sudo systemctl enable openvswitch-switch
sudo systemctl start openvswitch-switch

# Install Python3 and pip (required for Ryu)
sudo apt-get install -y python3 python3-pip

# Install Ryu SDN controller
sudo pip3 install ryu

# Create a simple Open vSwitch bridge
#sudo ovs-vsctl add-br br0
#sudo ovs-vsctl add-port br0 eth1  # Replace 'eth1' with the appropriate interface if needed

# Run the Ryu controller (example with a simple_switch application)
# Uncomment the following line to start the Ryu controller automatically
# ryu-manager ryu.app.simple_switch &

echo "SDN switch with Open vSwitch and Ryu controller setup completed."