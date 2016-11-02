import paramiko
import cmd
import time
import socket
import threading
import pdb
from exception import *
import logging_helper

logger = logging_helper.set_logger('contrail_performance')

class ssh_remote(object):
    """ Simple class to run commands remotely through an ssh channel """
    def __init__(self):
        self.hosts = []
        self.connections = []
    
    def add_host_info(self, args):
        """Add the host to the host list
            Usage Info:
            add_host_info([{'ip': "a.b.c.d", "username": "hello", "password": "hey"}])
        """
        if args:
            for host in args:
                self.hosts.append(host)
                logger.info("Method: add_host_info Describe: Added host {0} details".format(host['ip']))
        else:
            logger.warn("usage: add_host_info([{'ip': 'a.b.c.d', 'username': 'hello', 'password': 'hey'}])")
            raise ArguementError()
        
    def connect_to_hosts(self):
        """Connect to all hosts in the hosts list"""
        
        logger.info("Method: connect_to_hosts")
        for host in self.hosts:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host['ip'],username=host['username'],password=host['password'])
            self.connections.append(client)
    
    def execute_iperf(self, host=None, host_type='server', l4Type='udp', udpBw='10M', timeout=10, server=None):
        
        if host:
            pass
        else:
            logger.warn("Enter host arguemnt which is mandatory")
            raise ArguementError()
        
        host_type = host_type.upper()
        l4Type = l4Type.upper()
        
        if l4Type == 'UDP':
            iperf_cmd = 'iperf -u'
        elif l4Type == 'TCP':
            iperf_cmd = 'iperf'
        else:
            logger.warn('Unexpected l4 type: %s' %l4Type)
            raise UsageError()
        
        if host_type == 'SERVER':
            iperf_cmd += ' -s'
        elif host_type == 'CLIENT' and l4Type == 'TCP':
            iperf_cmd += ' -t {0} -c {1}'.format(timeout, server)
        elif host_type == 'CLIENT' and l4Type == 'UDP':
            iperf_cmd += ' -t {0} -c {1} -b {2}'.format(timeout, server, udpBw)
        else:
            logger.error("returning from execute_iperf")
            return
        
        self.execute_command_print(host, iperf_cmd)
    
    def find_conn(self, host_ip):
        
        for host, conn in zip(self.hosts, self.connections):
            if host_ip == host['ip']:
                return conn
        
        logger.error("Connection not found")
        logger.error("host_ip not found in the connections, please use add_host_info method and then try executing the command")
        return
    
    def execute_command_print(self, host_ip, command):
        """Execute this command on all hosts in the list"""
        
        host_found = False
        if command:
            conn = self.find_conn(host_ip)
            
            if command.startswith('iperf'):
                logger.info("Killing iperf process if avilable in host: {0} \n".format(host_ip))
                self._kill_iperf(conn)
                stdin, stdout, stderr = conn.exec_command(command, timeout=20)
                
                try:
                    for line in stdout:
                        logger.info('host: %s: %s' % (host_ip, line))
                    for line in stderr:
                        logger.warn('host: %s: %s' % (host_ip, line))
                except socket.timeout as error:
                    logger.debug("socket.timeout doesn't give an error message")
                    return
                
            if command.startswith('iperf'):
                self._kill_iperf(conn)
            else:
                logger.warn("usage: execute('ifconfig') ")
                raise UsageError()

    def _kill_iperf(self, conn):
        
        stdin, stdout, stderr = conn.exec_command('ps -e | grep iperf')
        for line in stdout:
            pid = line.split()[0]
            conn.exec_command('kill -9 {0}'.format(pid))
            logger.info("iperf process found and killed")
        time.sleep(0.1)
    
    def close_connections(self):
        for conn in self.connections:
            conn.close()
