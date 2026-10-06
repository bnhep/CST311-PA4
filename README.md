# Mininet Subnet Routing and Group Chat

This project is a computer networking assignment that combines IPv4 subnet design, Mininet network configuration, static routing, and a multiclient TCP chat application. The network connects four hosts through two switches and three legacy routers. The completed setup allows every host and router to communicate across the topology and allows three clients to participate in a group chat through a server running on one of the Mininet hosts.

## Project Goals

- Build and configure a Mininet network from a provided legacy-network starter file.
- Design two host subnets and two point-to-point router subnets.
- Configure router interfaces and static routes.
- Verify connectivity using Mininet commands such as `dump`, `links`, `nodes`, and `pingall`.
- Extend a two-client chat program to support three simultaneous clients.
- Automatically launch the chat server and clients in Mininet xterm windows.

## Network Topology

The topology contains:

- Hosts `h1` and `h2` connected to switch `s1`
- Hosts `h3` and `h4` connected to switch `s2`
- Router `r3` connecting the first host subnet to the router network
- Router `r4` connecting the two router links
- Router `r5` connecting the second host subnet to the router network

### Addressing Plan

| Node or link | Addressing |
|---|---|
| `h1` | `10.0.10.1/24` |
| `h2` | `10.0.10.2/24` |
| `r3` interface on `s1` | `10.0.10.3/24` |
| `h3` | `10.0.20.1/24` |
| `h4` | `10.0.20.2/24` |
| `r5` interface on `s2` | `10.0.20.3/24` |
| `r3`–`r4` link | `192.168.10.0/30` |
| `r3-eth1` | `192.168.10.2/30` |
| `r4-eth2` | `192.168.10.1/30` |
| `r4`–`r5` link | `192.168.20.0/30` |
| `r4-eth1` | `192.168.20.1/30` |
| `r5-eth1` | `192.168.20.2/30` |

The hosts use default routes through their local router. Static routes on `r3`, `r4`, and `r5` direct traffic to the remote host subnet and the opposite router link.

## Group Chat Service

The chat application uses TCP sockets and supports three clients simultaneously:

- **Server:** `h4` at `10.0.20.2`, listening on TCP port `12000`
- **Client 1:** `h1`
- **Client 2:** `h2`
- **Client 3:** `h3`

The server creates a dedicated thread for each client connection and uses a thread lock to safely manage the shared client list. Connected clients are assigned names such as `Client X`, `Client Y`, and `Client Z`. Messages are broadcast to the other connected clients, and the `bye` command removes a client from the chat and notifies the remaining participants.

The client uses separate sending and receiving threads so users can type messages while receiving messages from other participants.

## Files

- `legacy_network.py` – Creates the Mininet topology, configures IP addresses and routes, launches xterms, and starts the chat programs.
- `pa4_chat_server.py` – Threaded TCP group-chat server.
- `pa4_chat_client.py` – Concurrent TCP chat client with sending and receiving threads.
- `network_design.png` or `network_design.pdf` – Labeled topology diagram, if included.
- `network_changes.txt` – Explanation of changes made to the starter network file, if included.

## Requirements

- Linux environment with Mininet installed
- Open vSwitch and an X11 environment for Mininet terminals
- Python 2-compatible `python` command for the legacy Mininet script
- Python 3 for the chat server and client programs

## Running the Network

Run the Mininet setup script with the environment-isolation flag required by the assignment:

```bash
sudo -E python legacy_network.py
```

The script starts the topology, configures routing, and opens four xterm windows. The `h4` terminal runs the server, while the `h1`, `h2`, and `h3` terminals run clients.

Within the Mininet CLI, use the following commands to inspect and test the network:

```text
nodes
links
dump
pingall
```

`pingall` should show successful communication among the hosts and routers. In the chat windows, send at least one message from each client and verify that the other two clients receive it. Type `bye` in each client window to exit the chat session.

## Networking Concepts Demonstrated

- IPv4 subnetting with `/24` and `/30` networks
- Private IPv4 addressing
- Point-to-point router links
- Host default routes
- Router static routes
- IP forwarding on Linux-based routers
- Mininet switches, hosts, links, and xterm terminals
- TCP socket communication
- Concurrent client handling with Python threads
- Thread synchronization using locks
- Broadcast messaging to multiple connected clients
- Network validation with `pingall`

## Project Information

- Course: CST 311 – Introduction to Computer Networks
- Assignment: Programming Assignment 4 – Subnet Addressing and Group Chat
- Language: Python
- Protocol: TCP
- Chat port: `12000`
