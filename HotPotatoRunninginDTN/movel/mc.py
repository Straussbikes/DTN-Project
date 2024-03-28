#!/usr/bin/env python
#
# Send/receive UDP multicast packets.
# Requires that your OS kernel supports IP multicast.
#

MYPORT = 8123
MYGROUP_4 = '225.0.0.250'
MYGROUP_6 = 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'
MYTTL = 10 # Increase to reach other networks

import time
import struct
import socket
import sys, getopt
import fcntl

def main(argv):
    group = MYGROUP_4
    port = MYPORT
    action = 0
    interface = None

    try:
      opts, args = getopt.getopt(argv,"s6i:",["inf="])
    except getopt.GetoptError:
      print ('wrong input')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-s':
         action = 1
      elif opt == '-6':
         group = MYGROUP_6
      elif opt in ("-i", "--inf"):
         interface = arg

    if action == 0:
        # multicast receiver
       mcreceiver(group, interface)
    else:
        # multicast sender
       mcsender(group, interface)


def mcsender(group, interface,aenviar):
    addrinfo = socket.getaddrinfo(group, None)[0]

    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    # Set Time-to-live (optional)
    ttl_bin = struct.pack('@i', MYTTL)
    if addrinfo[0] == socket.AF_INET: # IPv4
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    else:
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)

    if interface != None:
        s.setsockopt(socket.SOL_SOCKET, 25, interface)

    
    data = aenviar
    s.sendto(data, (addrinfo[4][0], MYPORT))
    time.sleep(1)

def mcreceiver(group, interface):
    # Look up multicast group address in name server and find out IP version
    addrinfo = socket.getaddrinfo(group, None)[0]

    # Create a socket
    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

    # Allow multiple copies of this program on one machine
    # (not strictly needed)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind it to the port
    s.bind(('', MYPORT))

    group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
    # Join group
    mreq = group_bin
    if addrinfo[0] == socket.AF_INET: # IPv4
        if interface == None:
            mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
        else:
            ip_addr = get_ip_address(interface)
            ip_addr_n = socket.inet_aton(ip_addr)
            mreq = group_bin + struct.pack("=4s", ip_addr_n)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    else:
        if interface == None:
            mreq = group_bin + struct.pack('@I', 0)
        else:
            #TODO: need fully test
            ip_addr = get_ip_address(interface)
            ip_addr_n = socket.inet_aton(ip_addr)
            mreq = group_bin + struct.pack("=4s", ip_addr_n)
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

    # Loop, printing any data we receive
   
    data, sender = s.recvfrom(1500)
    return data
    #print(data)

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
