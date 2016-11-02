from performance.src.iperf_manage import perform_iperf_check
from performance.src.netem_controller import netem_controller
import time

def main():
    #creates instance of netem_controller class
    cp = netem_controller()
    #instantiates perform_iperf_check class
    p = perform_iperf_check()
    #add interface details like below
    cp.add_interface_netem_details( p514p2 = {'ip_address': 'fe80::92e2:baff:fe84:520f', 'delay': 20, 'loss': 0.1})
    #set netem attribute (This is the step when interface p514p2 will be ste with the respective delay and packet loss values)
    cp.set_netem_attributes()
    #show netem attributes verifies whether the value has been set
    cp.show_netem_attributes()

    #iperf method will help to remotely ssh to the two host(bm/machones/containers) and does the udp bandwidth test and provides a result
    p.iperf(server_details={'ip': '1.1.1.1', 'username': 'root', 'password': 'password123'}, client_details={'ip': '2.2.2.2', 'username': 'root', 'password': 'password123'}, udpBw='1000M')

    time.sleep(20)

