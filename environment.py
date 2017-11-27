import subprocess
import os
import sys
import time
import paramiko
import pycurl
from io import BytesIO
from urllib.parse import urlencode
import json








class env():

    def createlinkovs(self, IPSDN="192.168.122.208", IPC1="192.168.122.134", IPC2="192.168.122.135"):

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(destIP, username='root', password='iprotect')

        basiCmd = 'ovs-vsctl add-br OvsDc1'
        os.system(basiCmd)

        basiCmd = 'ovs-vsctl add-br OvsClt'
        os.system(basiCmd)

        basiCmd = 'ovs-vsctl add-br OvsDc0'
        stdin, stdout, stderr = ssh.exec_command(basiCmd)
        result = stdout.read()
        stdin.flush()

        basiCmd= 'ovs-vsctl set-controller OvsClt tcp:'+str(IPSDN)+':6653'
        os.system(basiCmd)

        basiCmd = 'ovs-vsctl set-controller OvsDc1 tcp:'+str(IPSDN)+':6653'
        os.system(basiCmd)

        basiCmd = 'ovs-vsctl add-port OvsDc1 gre0 -- set interface gre0 type=gre options:remote_ip='+str(IPC2)
        os.system(basiCmd)

        basiCmd = 'ovs-vsctl add-port OvsClt vxlan0 -- set interface vxlan0 type=vxlan options:remote_ip='+str(IPC2)
        os.system(basiCmd)

        basiCmd = 'ovs-vsctl set-controller OvsDc0 tcp:'+str(IPSDN)+':6653'
        stdin, stdout, stderr = ssh.exec_command(basiCmd)
        result = stdout.read()
        stdin.flush()

        basiCmd = 'ovs-vsctl add-port OvsDc0 gre0 -- set interface gre0 type=gre options:remote_ip='+str(IPC1)
        stdin, stdout, stderr = ssh.exec_command(basiCmd)
        result = stdout.read()
        stdin.flush()

        basiCmd = 'ovs-vsctl add-port OvsDc0 vxlan0 -- set interface vxlan0 type=vxlan options:remote_ip='+str(IPC1)
        stdin, stdout, stderr = ssh.exec_command(basiCmd)
        result = stdout.read()
        stdin.flush()


        basiCmd = 'ip link add name vethCltDc1 type veth peer name vethDc1Clt'
        os.system(basiCmd)
        basiCmd = 'ip link set vethDc1Clt up'
        os.system(basiCmd)
        basiCmd = 'ip link set vethCltDc1 up'
        os.system(basiCmd)
        basiCmd = 'ovs-vsctl add-port OvsClt vethCltDc1 -- set Interface'
        basiCmd = basiCmd + ' vethCltDc1 ofport_request=11'
        os.system(basiCmd)
        basiCmd = 'ovs-vsctl add-port OvsDc1 vethDc1Clt -- set Interface'
        basiCmd = basiCmd + ' vethDc1Clt ofport_request=11'
        os.system(basiCmd)
        ssh.close()


        '''
        for line in open(LXC_PATH + str(containerName) + '/config', "r"):
            if "lxc.cgroup.cpuset.cpus" in line:
                pass'''
    def start(self, containerName):
        try:
            print("container starting :")
            basiCmd = 'lxc-start -n ' + str(containerName)
            os.system(basiCmd)
            return 1
        except Exception as exception:
            return 0

    def info(self, containerName):
        try:
            basiCmd = 'lxc-info -n ' + str(containerName)
            result = subprocess.check_output(basiCmd, shell=True)
            return result
        except:

            print("unable to get specific information about the container")
            return NOK

    def getPIDstr(self, containerName):
        try:
            resultInfo = self.info(containerName)
            myInfo = resultInfo.decode().split('\n')
            containerStatus = myInfo[1].replace(' ', '').split(':')[1]

            # Must implement remote verify
            if (containerStatus == 'STOPPED'):
                # self.copy(containerName, destIP, migType)
                print("container is stopped")
                return NOK
            if (containerStatus == 'RUNNING'):
                strContainerPID = myInfo[2].replace(' ', '').split(':')[1]
                return str(strContainerPID)
        except:

            print("unable to get PID information about the container")

    def createClient(self, containerName="C17"):
        LXC_PATH = "/var/lib/lxc/"

        print("container creation :")
        #basiCmd = 'lxc-create -t ubuntu -n ' + str(containerName) + ' -- -r trusty -a amd64'
        #os.system(basiCmd)
        basiCmd = 'lxc-copy -n nginxBKclient -N ' + containerName
        os.system(basiCmd)
        print("### clone done ###")
        with open(LXC_PATH + str(containerName) + '/config', "a") as myfile:
            myfile.write('\n# hax for criu\n')
            myfile.write('lxc.console = none\n')
            myfile.write('lxc.tty = 0\n')
            myfile.write('lxc.cgroup.devices.deny = c 5:1 rwm\n')
        for line in open(LXC_PATH + str(containerName) + '/config', "r"):
            if "lxc.network.link" in line:
                with open(LXC_PATH + str(containerName) + '/config', "r") as input:
                    with open(LXC_PATH + str(containerName) + '/config2', "w") as output:
                        for line2 in input:
                            if line2 != line:
                                output.write(line2)

                basiCmd = 'rm ' + LXC_PATH + str(containerName) + '/config'
                os.system(basiCmd)
                basiCmd = 'mv ' + LXC_PATH + str(containerName) + '/config2 ' + LXC_PATH + str(containerName) + '/config'
                os.system(basiCmd)
        print("first step end")
        with open(LXC_PATH + str(containerName) + '/config', "a") as myfile:
            myfile.write('\nlxc.network.link =')
            myfile.write(' ')
            myfile.write(str("br" + containerName))
            myfile.write('\n')
        print("second step end")

        basiCmd = "ip link add name veth" + str(containerName) + "Ovs type veth peer name vethOvs" + str(containerName)
        os.system(basiCmd)

        basiCmd = "ip link set vethOvs" + str(containerName) + " up"
        os.system(basiCmd)

        basiCmd = "ip link set veth" + str(containerName) + "Ovs up"
        os.system(basiCmd)

        basiCmd = "brctl addbr br" + str(containerName)
        os.system(basiCmd)

        basiCmd = "ifconfig br" + str(containerName) + " up"
        os.system(basiCmd)

        basiCmd = "brctl addif br" + str(containerName) + " veth" + str(containerName) + "Ovs"
        os.system(basiCmd)

        basiCmd = "sudo ovs-vsctl add-port OvsClt vethOvs" + str(containerName) + " -- set Interface vethOvs" + str(containerName) + " ofport_request=12"
        os.system(basiCmd)

        for line in open(LXC_PATH + str(containerName) + '/rootfs/etc/network/interfaces', "r"):
            if "iface eth0 inet dhcp" in line:
                with open(LXC_PATH + str(containerName) + '/rootfs/etc/network/interfaces', "r") as input:
                    with open(LXC_PATH + str(containerName) + '/rootfs/etc/network/interfaces2', "w") as output:
                        for line2 in input:
                            if line2 != line:
                                output.write(line2)

                basiCmd = 'rm ' + LXC_PATH + str(containerName) + '/rootfs/etc/network/interfaces'
                os.system(basiCmd)
                basiCmd = 'mv ' + LXC_PATH + str(containerName) + '/rootfs/etc/network/interfaces2 ' + LXC_PATH + str(containerName) + '/rootfs/etc/network/interfaces'
                os.system(basiCmd)

                with open(LXC_PATH + str(containerName) + '/rootfs/etc/network/interfaces', "a") as myfile:
                    myfile.write('\niface eth0 inet static')
                    myfile.write('\n    address ')
                    myfile.write('172.16.207.12')
                    myfile.write('\n')
                    myfile.write('    netmask 255.255.255.0')

        with open(LXC_PATH + str(containerName) + '/rootfs/etc/network/interfaces', "a") as myfile:
            myfile.write('\nauto vethCltOut')
            myfile.write('\niface vethCltOut inet static')
            myfile.write('\n    address ')
            myfile.write('192.168.0.18')
            myfile.write('\n')
            myfile.write('    netmask 255.255.255.0')
            myfile.write('\n')
            myfile.write('    gateway 192.168.0.2')



        self.start(containerName)

        ####################################################################################
        ##################################second interface##################################
        ####################################################################################


        basiCmd = 'brctl addbr brOut'
        os.system(basiCmd)

        # basiCmd = 'ifconfig brOut 10.10.10.1 netmask 255.255.255.0 up'
        basiCmd = 'ifconfig brOut 192.168.0.2 netmask 255.255.255.0 up'
        os.system(basiCmd)
        # Forward brOut to Internet
        basiCmd = 'iptables -t nat -A POSTROUTING --out-interface ens33 -j MASQUERADE'
        os.system(basiCmd)
        basiCmd = 'iptables -A FORWARD --in-interface brOut -j ACCEPT'
        os.system(basiCmd)

        basiCmd = 'ip link add name vethCltOut type veth peer name vethOutClt'
        os.system(basiCmd)
        basiCmd = 'ip link set vethCltOut up'
        os.system(basiCmd)
        basiCmd = 'ip link set vethOutClt up'
        os.system(basiCmd)
        basiCmd = 'brctl addif brOut vethOutClt'
        os.system(basiCmd)
        cltPID = self.getPIDstr(containerName)
        basiCmd = 'ip link set dev vethCltOut netns '
        basiCmd = basiCmd + cltPID + ' name vethCltOut'
        os.system(basiCmd)
        
g=env.createlinkovs()
t=env.createClient()
        
