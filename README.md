#Performance Sanity
Modules which will help to check the performance of an application/software.

##Overview

Performance sanity project gives you set of core modules which will help you in emulating a production network (interms of latency, packet loss) and does the performance evaluation of your application using iperf.

There are two important modules:
* netem_controller
* iperf_manage

##Caveats

Works only on linux operating system

##prerequisites
* [iperf tool](https://iperf.fr/iperf-download.php)
* [python paramiko](http://www.paramiko.org/installing.html)

##netem_controller

This module helps in emulating the production setup network by introducing delay and packet loss on the interface through which your application is connected to internet. We can inject these dealys and packet loss into multiple interface as well. Below is the snippet of how can we create a network emulation on the interface 'p514p2'. There are more samples in the sample directory.
```
    #creates instance of netem_controller class
    cp = netem_controller()
    #add interface details like below
    cp.add_interface_netem_details( p514p2 = {'ip_address': 'fe80::92e2:baff:fe84:520f', 'delay': 20, 'loss': 0.1})
    #set netem attribute (This is the step when interface p514p2 will be ste with the respective delay and packet loss values)
    cp.set_netem_attributes()
    #show netem attributes verifies whether the value has been set
    cp.show_netem_attributes()
    time.sleep(2)
    #unset netem attributes will reset(remove) the previously set netem attributes
    cp.unset_netem_attributes()
```

##iperf_manage

This module uses iperf tool which actively measures the maximum achievable bandwidth on IP networks. It logins remotely to two device, one device will act as an iperf client and other device will be an iperf server. We can tune the transport protocol and the speed at which we send packets. Below is the snippet of how can we use iperf_manage module. There are more samples in sample directory(Work in Progress).

```
    p = perform_iperf_check()
    #iperf method will help to remotely ssh to the two host(bm/machones/containers) and does the udp bandwidth test and provides a result
    p.iperf(server_details={'ip': '2.2.2.2', 'username': 'root', 'password': 'password123'}, client_details={'ip': '1.1.1.1', 'username': 'root', 'password': 'password123'}, udpBw='1000M')
``` 
Iperf method will display bandwith, jitter and packet loss at the end of the test.

##Advanced usage

Combination of the above two modules will give a good way to test performance of any application. Use netem_controller to introduce delay and packet loss in the network, then use the iperf_manage module to check the performance of application at a particular transmission speed. Refer the sample_usage_netem_iperf.py module in the sample directory.
