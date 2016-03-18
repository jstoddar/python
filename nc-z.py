#!/usr/bin/env python
'''
nc-z.py: script to check to see if port is open.
Handy to have where you can't install nc or nmap.
Output and status largely mimic "nc -z".
'''
import sys, re, socket
from contextlib import closing
SCRIPT_NAME = sys.argv[0]
# jstoddar at g mail .com
# The -z option to nc has annoyingly turned up missing in rhel7 nc
#  and clone versions.
# Output intended to "fool" bash scripts that formerly used
#  nc -z [-v] [-w nseconds] <host> <port>
# If you like, you can wrapper nc and use this script when
#  the "-z" prameter is passed to nc. This ugliness is up to you.

def usage():
    ''' Usage function '''
    print "Usage: " + SCRIPT_NAME + \
    " [-v|--verbose] [-w|-t|--timeout nseconds] <hostname> <port>"
    print "example: " + SCRIPT_NAME + " -v localhost 222 -w 2.0"
    sys.exit(2)

def parse_input():
    ''' Parse input args. '''
    v = False
    t = 1.0 # default timeout, note nc defaults to no timeout.
    args = []
    rargs = sys.argv[1:]
    for arg in rargs:
        if arg == '-z':
            continue
        if arg in ['-v', '-zv', '-vz', '--verbose']:
            v = True
        elif arg in ['-w', '-t', '--timeout']:
            t = rargs[rargs.index(arg) + 1]
        elif arg != t:
            args.append(arg)
    return v, t, args

def get_port_service(port):
    ''' Get service name for port out of /etc/services. '''
    regex_out = '*'
    with open("/etc/services") as f:
        for line in f:
            search_regex = r"(^[a-z]+)((-[a-z]+)*)(\s+)" \
             + re.escape(port) + r"(\s+)"
            if re.match(search_regex, line):
                regex_out = line.split("\t", 1)[0]
        return regex_out

def ck_socket(host, port, timeout):
    '''
    Open and check the socket:port.
    Note: Returns shell true "0" if connect was successful, if not, "1".
    '''
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(float(timeout))
        return sock.connect_ex((host, int(port)))

def verbose_output(sock_status, host, port):
    '''
    Output strings and exit values close enough to perhaps work
     with some bash scripts formally using "nc -x to test ports."
    '''
    if sock_status == 0:
        service = get_port_service(port + "/tcp")
        print "Connection to " + host + " " + port \
         + " port [tcp/" + service + "] succeeded!"
    else:
        print SCRIPT_NAME + ": connect to " + host \
         + " port " + port + " (tcp) failed: "

def main():
    verbose, timeout, params = parse_input()
    if len(params) == 2:
        host, port = params
        sock_status = ck_socket(host, port, timeout)
    else:
        usage()
    if verbose:
        verbose_output(sock_status, host, port)
    if sock_status != 0:
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
