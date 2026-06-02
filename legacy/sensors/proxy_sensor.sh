#!/bin/bash
# Decentralized Sensor Proxy Script
# This script turns any Linux server into a silent honeypot sensor by using iptables 
# to forward traffic on unused ports back to the central Sentinels cluster.

# Configuration
CENTRAL_HONEYPOT_IP="10.99.1.50" # Replace with your central Sentinels LoadBalancer/EKS IP

echo "Setting up Decentralized Sentinels Sensor..."

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1

# List of ports to forward (FTP, SSH, Telnet, HTTP, SMB)
# CAUTION: Ensure these ports are NOT used by the production services on this machine!
PORTS=(21 2222 23 8080 445)

for PORT in "${PORTS[@]}"; do
    echo "Forwarding traffic on port $PORT to $CENTRAL_HONEYPOT_IP:$PORT"
    
    # PREROUTING: Send incoming traffic to the central honeypot
    iptables -t nat -A PREROUTING -p tcp --dport $PORT -j DNAT --to-destination $CENTRAL_HONEYPOT_IP:$PORT
    
    # POSTROUTING: Masquerade so the response comes back through this sensor
    iptables -t nat -A POSTROUTING -p tcp -d $CENTRAL_HONEYPOT_IP --dport $PORT -j MASQUERADE
done

echo "Sensor proxy setup complete! All scans hitting these ports will be silently funneled to Sentinels."
