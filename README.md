# PBL Connected Robots

## Description

This part attempts to observe the latency and packet loss rates of Franka Emika robots, it is **based on the [Libfranka](https://frankaemika.github.io/docs/libfranka.html)** and **[Frankx](https://github.com/pantor/frankx)** .

## Requirements

1. Franka Emika robots and controller

2. Hosts connected to the controller

3. Wireshark on the hosts

## Getting Started

### Step1. Run the Orchestration.py on hosts

 1. Unlock the robots.
 2. Set master robot to manual control mode.
 3. Run the Orchestration.py on hosts.

### Part2. Packet capture

Packet capture is done by **[Wireshark](https://www.wireshark.org/)**. Run wireshark on all hosts and capture packets between hosts.

### Part3. Analysis of captured packets

 1. Run getdata.py to get the data corresponding to each Identification code.
 2. Export data from wireshark as a csv file. Each column is the serial number, time, source, destination, Protocol, Identification and Frame length.
 3. Run Data_Analyze.py and plot.py to get the Result.
