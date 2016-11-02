from performance.src.netem_controller import netem_controller
import time

def single_interface_netem_attributes():
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

def multiple_interface_netem_attributes():

    #creates instance of netem_controller class
    cp = netem_controller()
    #add interface details like below
    cp.add_interface_netem_details( p514p2 = {'ip_address': 'fe80::92e2:baff:fe84:520f', 'delay': 20, 'loss': 0.1}, eth0 = {'ip_address': 'fe80::b4ee:50ff:fef0:20c3', 'delay': 10})
    #set netem attribute (This is the step when interface p514p2 will be ste with the respective delay and packet loss values)
    cp.set_netem_attributes()
    #show netem attributes verifies whether the value has been set
    cp.show_netem_attributes()
    time.sleep(2)
    #unset netem attributes will reset(remove) the previously set netem attributes
    cp.unset_netem_attributes()
