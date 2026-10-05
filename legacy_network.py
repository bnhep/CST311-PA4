#!/usr/bin/python
"""
Brandon Nhep
CST 311, Introduction to Computer Networks
Programming Assignment 4
10/25/2025
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from mininet.term import makeTerm
from subprocess import call
from time import sleep

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/24')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    # Assigned ip for routers
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    # Part of subnet 10.0.20.0/24 with h3 and h4
    r5 = net.addHost('r5', cls=Node, ip='10.0.20.3/24')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')
    r4 = net.addHost('r4', cls=Node, ip='192.168.10.1/30')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')
    # Part of subnet 10.0.10.0/24 with h1 and h2
    r3 = net.addHost('r3', cls=Node, ip='10.0.10.3/24')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Assigned ip for hosts
    # h1 and h2 are in subnet 10.0.10.0/24
    # h3 and h4 are in subnet 10.0.20.0/24
    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.10.1/24', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.10.2/24', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.20.1/24', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.20.2/24', defaultRoute=None)

    info( '*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)
    net.addLink(s2, r5)
    net.addLink(s1, r3)
    # Added links for the routers
    # This adds a link between r3 and r4 with interface names and IP addresses
    # interface 1 on r3 is r3-eth1 with IP 192.168.10.2/30
    # interface 2 on r4 is r4-eth2 with IP 192.168.10.1/30
    net.addLink(r3, r4, intfName1='r3-eth1', params1={'ip': '192.168.10.2/30'},
                intfName2='r4-eth2', params2={'ip': '192.168.10.1/30'})

    # This adds a link between r4 and r5 with interface names and IP addresses
    # interface 1 on r4 is r4-eth1 with IP 192.168.20.1/30
    # interface 2 on r5 is r5-eth1 with IP 192.168.20.2/30
    net.addLink(r4, r5, intfName1='r4-eth1', params1={'ip': '192.168.20.1/30'},
                intfName2='r5-eth1', params2={'ip': '192.168.20.2/30'})

    info( '*** Starting network\n')
    net.build()

    # Adding routes to r3 r5 default routes using command line executing
    # Host h1,h2 to r3 - h3,h4 to r5
    h1.cmd('ip route add default via 10.0.10.3')
    h2.cmd('ip route add default via 10.0.10.3')
    h3.cmd('ip route add default via 10.0.20.3')
    h4.cmd('ip route add default via 10.0.20.3')

    # Router r3 to h3,h4, hop via r4, from r3-eth1
    r3.cmd('ip route add 10.0.20.0/24 via 192.168.10.1 dev r3-eth1')
    # Router r3 to r4-r5 link, hop to r4, from r3-eth1
    r3.cmd('ip route add 192.168.20.0/30 via 192.168.10.1 dev r3-eth1')

    # Router r5 to h1,h2 hop via r4, from r5-eth1
    r5.cmd('ip route add 10.0.10.0/24 via 192.168.20.1 dev r5-eth1')
    # Router r5 to r3-r4 link, hop to r4, from r5-eth1
    r5.cmd('ip route add 192.168.10.0/30 via 192.168.20.1 dev r5-eth1')

    # Router r4 to h1,h2, hop to r3-eth1, from r4-eth2
    r4.cmd('ip route add 10.0.10.0/24 via 192.168.10.2 dev r4-eth2')
    # Router r4 to h3,h4, hop to r5-eth1, from r4-eth1
    r4.cmd('ip route add 10.0.20.0/24 via 192.168.20.2 dev r4-eth1')

    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s2').start([c0])
    net.get('s1').start([c0])

    # Starting x-terms for hosts to run server and clients code
    # Sleep calls are to prevent terminals from overlapping and assigning
    # wrong clients to wrong terminals
    info( '*** Post configure switches and hosts\n')
    makeTerm(h4, title='Node', term='xterm', display=None, cmd='python3 pa4_chat_server.py; bash')
    sleep(0.2)
    makeTerm(h1, title='Node', term='xterm', display=None, cmd='python3 pa4_chat_client.py; bash')
    sleep(0.2)
    makeTerm(h2, title='Node', term='xterm', display=None, cmd='python3 pa4_chat_client.py; bash')
    sleep(0.2)
    makeTerm(h3, title='Node', term='xterm', display=None, cmd='python3 pa4_chat_client.py; bash')

    CLI(net)
    net.stop()
    # added it to stop x-terms after exiting CLI
    net.stopXterms()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()