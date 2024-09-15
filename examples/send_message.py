import argparse
import meshtastic.tcp_interface

mesh_interface = meshtastic.tcp_interface.TCPInterface(hostname='192.168.1.151')

def onResp():
    print("yo")

def main():
    mesh_interface.sendText(text="test CLI python message", destinationId="!e2e18960", wantAck=True, onResponse=onResp, channelIndex=0)

if __name__ == "__main__":
    main()
