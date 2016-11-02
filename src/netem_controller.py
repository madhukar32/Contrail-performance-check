"""
This program contains the code for tweaking the latency and packet loss of a list of interfaces using netem for performance check of applications
"""

from pyroute2 import IPRoute

from pyroute2.netlink.rtnl import RTM_DELQDISC
from pyroute2.netlink.rtnl import RTM_NEWQDISC
from pyroute2.netlink.rtnl import RTM_GETQDISC

from exception import *

import sys
import pdb
import re
import logging_helper


TIME_UNITS_PER_SEC = 1000000

_psched = open('/proc/net/psched', 'r')
[_t2us,
_us2t,
_clock_res,
_wee] = [int(i, 16) for i in _psched.read().split()]
_clock_factor = float(_clock_res) / TIME_UNITS_PER_SEC
_tick_in_usec = float(_t2us) / _us2t * _clock_factor
_first_letter = re.compile('[^0-9]+')
_psched.close()

def _time2tick_to_time(time2tick):
    #reverse of _time2tick from pyroute2.netlink.rtnl.tcmsg
    return int(time2tick/_tick_in_usec)


def _u32topercent(u32):
    #reverse of _percent2u32 function from pyroute2.netlink.rtnl.tcmsg
    return round(u32*100/float(2**32-1), 3)


class netem_controller(object):
    """ Contrail performance class
        Usage:
        cp = netem_controller()
    """
    def __init__(self, *args):
        self.logger = logging_helper.set_logger('netem_controller')
        self.intf_details = []
	self.iproute = IPRoute()
        self.netem_return = {}        

    def add_interface_netem_details(self, **kwargs):

        """ Method to add interface for which you need to change the latency and loss attributes 
            Usage:
            cp.add_interfacenetem_details({"p4p1": {ip_address: 'fe80::dcdc:1bff:fea0:4dfe', delay: 20, loss: 0.1}, 
					   "p4p2": {ip_address: 'fe80::dcdc:1bcc:fc70:4dfe', delay: 20, loss: 0.1}})
        """
        
        if not kwargs:
            warn_msg = "Method: add_interface_netem_details Details: Forgot to provide arguement for this method. Check samples directory to few samples of arguement"
            self.logger.warn(warn_msg)
            raise ArguementError()
        
        for intf in kwargs:
            self.logger.info("Interface: {} is being added ".format(intf))
            
            try:
                intf_id = self._get_intf_index_using_intf(intf)
            except IndexError:
                ip_address = kwargs[intf].get('ip_address', None)
                if not ip_address:
                    warn_msg = "Method: add_interface_netem_details Details: ipv4/ipv6 address is not provided"
                    self.logger.warn(warn_msg)
                    raise UsageError()
                else:
                    try:
                        intf_id = self._get_intf_index_using_ipaddress(ip_address)
                    except Exception as e:
                        warn_msg = "Method: add_interface_netem_details intf: {0} error: {1} \n".format(intf, e)
                        self.logger.warn(warn_msg)
                        raise LabelError()
            except Exception:
                self.logger.error("Unknow Error: Traceback", exc_info=True)
            
            kwargs[intf]['index'] = intf_id
            kwargs[intf]['name'] = intf
            self.intf_details.append(kwargs[intf])
				

    def _check_loss(self, loss):

        """ Helper method to check if loss type and value are correct """

        if type(loss) == float:
            if loss < 90:
                return None
            else:
                error_msg = "Method: _check_loss Error: loss percentage exceeds 90 percent"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            error_msg = "Method: _check_loss Error: loss should be type float "
            self.logger.error(error_msg)
            raise TypeError(error_msg)

    def _get_intf_index_using_intf(self, intf):

        """ Helper method to get interface index using interface as an arguement """
        if not intf:
            warn_msg = "Method: _get_intf_index_using_intf Error: intf arguement is not provided"
            self.logger.warn(warn_msg)
            raise UsageError()
        
        return self.iproute.get_addr(label=intf)[0]['index']

    def _get_intf_index_using_ipaddress(self, ip_address):

        """ Helper method to get interface index using ip_address as an arguement """

        if not ip_address:
            warn_msg = "Method: _get_intf_index_using_ip_address Error: ip_address arguement is not provided"
            self.logger.error(warn_msg)
            raise UsageError()
        return self.iproute.get_addr(address=ip_address)[0]['index']


    def _set_netem(self, **kwargs):

        """ Helper method to set netem attributes """
        #pdb.set_trace()
        delay = kwargs.get('delay')
        loss = kwargs.get('loss')
        intf_index = kwargs.get('intf_index')
        #self.netem_return = {} 
        
        try:
            ret = self.iproute.tc(RTM_NEWQDISC, 'netem', intf_index, 0, delay = delay * 1000, loss=loss)
            self.logger.info("Method: _set_netem ret:{0}".format(ret))
        except Exception:
            e = sys.exc_info()[0]
            self.logger.warn("Method: _set_netem  error: {0}".format(e))
            raise Pyroute2Error()
        
    def unset_netem_attributes(self, *interfaces):

        """ Method to unset netem attributes 
            Usage:
            cp.unset_netem_attributes()
        """

        for intf in self.intf_details:
            try:
                intf_index = intf.get('index')
                ret = self.iproute.tc(RTM_DELQDISC, 'netem', intf_index, 0)
                self.logger.info("Method: unset_netem_attributes intf:{0} ret:{1}\n".format(intf['name'], ret))
            except Exception:
                e = sys.exc_info()[0]
                self.logger.warn("Method: unset_netem_attribute intf: {0} error: {1}\n".format(intf['name'], e))
		raise Pyroute2Error()

    def set_netem_attributes(self):

        """Set netem attributes
           Usage:
           cp.set_netem_attributes()
        """
        #pdb.set_trace()
        for intf in self.intf_details:
            delay = intf.get('delay')
            loss = intf.get('loss')
            intf_index = intf.get('index')
            
            ret = None 
            try:
                if delay and loss:
                    ret=self._check_loss(loss)
                elif delay or loss:
                    if delay and not loss:
                        loss = float(0)
                    elif loss and not delay:
                        ret=self._check_loss(loss)
                        delay = 0
		else:
		    warn_msg = "Method: set_netem_attributes Error: Either delay or loss arguement should be specified"
                    self.logger.warn(warn_msg)
                    raise UsageErrorException()
            except Exception:
                self.logger.error("Oh hell! unexpected error. Here is the more info about it", exc_info=True)
            
            try:
                self._set_netem(delay = delay, loss = loss, intf_index=intf_index)
            except Exception:
                self.logger.error("Oops!. Info:", exc_info=True)

    def _get_delay_loss(self, netem_ret_dict):
        #Helps to get the converted delay and loss value
        
        delay_time2tick = netem_ret_dict[0]['attrs'][1][1]['delay']
        delay = _time2tick_to_time(delay_time2tick)/1000

        loss_u32 = netem_ret_dict[0]['attrs'][1][1]['loss']
        loss = _u32topercent(loss_u32)
        return delay, loss

    def show_netem_attributes(self):

        """ Displays current netem attributes
            cp.show_netem_attributes()
        """

        for intf in self.intf_details:
            try:
                intf_index = intf.get('index')
                ret = self.iproute.tc(RTM_GETQDISC, 'netem', intf_index, 0)
                delay, loss = self._get_delay_loss(ret)
                self.logger.debug("Method: show_netem_attributes intf:{0} ret:{1}\n".format(intf['name'], ret))
                self.logger.info("Display interface netem attributes for intf: {0}".format(intf['name']))
                self.logger.info("delay \t {0} ms".format(float(delay)))
                self.logger.info("packet loss \t {0}".format(loss))
            except Exception as e:
                warn_msg = "Method: show_netem_attributes intf: {0} error: {1}\n".format(intf['name'], e)
                self.logger.warn(warn_msg)
                raise Pyroute2Error()

#if __name__ == "__main__":
#	cp = netem_controller()
#	cp.add_interface_netem_details( p514p2 = {'ip_address': 'fe80::92e2:baff:fe84:520f', 'delay': 20, 'loss': 0.1})	
#	cp.set_netem_attributes()
#	cp.show_netem_attributes()
#	import time
#	time.sleep(2)
#	cp.unset_netem_attributes()
