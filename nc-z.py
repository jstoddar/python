#!/usr/bin/env python
import sys, re, socket
from contextlib import closing
SCRIPT_NAME = sys.argv[0]
# jstoddar at g mail .com
'''nc-z.py: script to check to see if port is open.
Handy to have where you can't install nc or nmap.
Output and status largely mimic "nc -z". '''

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
    with open("/etc/services") as f:
        for line in f:
            search_regex = r"(^[a-z]+)(\s+)" + re.escape(port) + r"(\s+)"
            if re.match(search_regex, line):
                return line.split("\t", 1)[0]

def ck_socket(host, port, timeout, verbose):
    '''
    Open and check the socket:port.
    Output strings and exit values close enough to work
     with some bash scripts formally using "nc -x to test ports."
    '''
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(float(timeout))
        if sock.connect_ex((host, int(port))) == 0:
            if verbose:
                service = get_port_service(port + "/tcp")
                print "Connection to " + host + " " + port \
                + " port [tcp/" + service + "] succeeded!"
            sys.exit(0)
        else:
            if verbose:
                print SCRIPT_NAME + ": connect to " + host \
                + " port " + port + " (tcp) failed: "
            sys.exit(1)

def main():
    verbose, timeout, params = parse_input()
    if len(params) == 2:
        host, port = params
        ck_socket(host, port, timeout, verbose)
    else:
        usage()

if __name__ == '__main__':
    sys.exit(main())
