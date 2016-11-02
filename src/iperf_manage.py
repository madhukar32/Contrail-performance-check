import os
import sys
from ssh_remote import *
import threading
import traceback
import pdb

#logger = logging_helper.set_logger('contrail_performance')

class perform_iperf_check():
    def __init__(self):
        self.ssh_server = ssh_remote()
        self.ssh_client = ssh_remote()
        
    def iperf(self, server_details=None, client_details=None, l4Type='udp', udpBw='10M', timeout=10):
        
        if server_details and client_details:
            pass
        else:
            logger.warn("Enter server and client IP arguemnt which are mandatory")
            raise ArguementError()
        
        try:
            pdb.set_trace()
            self.ssh_server.add_host_info([server_details])
            self.ssh_client.add_host_info([client_details])
            self.ssh_server.connect_to_hosts()
            self.ssh_client.connect_to_hosts()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            raise IperfError(''.join('!! ' + line for line in lines))
        
        self._thread_client_server(server=server_details['ip'], client=client_details['ip'], l4Type=l4Type, udpBw=udpBw, timeout=timeout)
        
        self.ssh_server.close_connections()
        self.ssh_client.close_connections()
    
    def _thread_client_server(self, server=None, client=None, l4Type='udp', udpBw='10M', timeout=10):
        
        if server and client:
            pass
        else:
            logger.warn("Enter server and client IP arguemnt which are mandatory")
            raise ArguementError()
        
        thread = []
        for i in range(2):
            if i == 0:
                thread.append(threading.Thread(target=self.ssh_server.execute_iperf, kwargs={'host': server, 'host_type': 'server', 'l4Type': l4Type, 'udpBw': udpBw, 'timeout': timeout}))
            else:
                thread.append(threading.Thread(target=self.ssh_client.execute_iperf, kwargs={'host': client, 'host_type': 'client', 'server': server, 'l4Type': l4Type, 'udpBw': udpBw, 'timeout': timeout}))
            
            thread[i].daemon = True
            thread[i].start()
                
        for i in range(2):
            thread[i].join()

