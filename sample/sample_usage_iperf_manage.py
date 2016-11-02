from performance.src.iperf_manage import perform_iperf_check

def using_iperf_manage():
    #instantiates perform_iperf_check class
    p = perform_iperf_check()
    #iperf method will help to remotely ssh to the two host(bm/machones/containers) and does the udp bandwidth test and provides a result
    p.iperf(server_details={'ip': '1.1.1.1', 'username': 'root', 'password': 'password123'}, client_details={'ip': '2.2.2.2', 'username': 'root', 'password': 'password123'}, udpBw='1000M')
