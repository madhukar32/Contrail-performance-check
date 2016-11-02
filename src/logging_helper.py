import logging
import logging.handlers



def set_logger(func_name, log_level='INFO'):
    """ Common logger function for all the modules  """
    logger = logging.getLogger(func_name)
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(fmt=formatter)
    logger.addHandler(ch)
    
    # create syslog handler and set level to debug
    sh = logging.handlers.SysLogHandler(address='/dev/log')
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(fmt=formatter)
    logger.addHandler(sh)
    
    filename='/var/log/' + func_name + '.log'
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    #ch = logging.StreamHandler()
    #ch.setLevel(logging.DEBUG)
    #ch.setFormatter(formatter)
    #logger.addHandler(ch)
    return logger
