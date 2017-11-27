
import sys
import os
import paramiko
import subprocess
import fileinput
import NothBoundLayer






class createNetwork():

    #bridge creation for each contsiner
    def modconfigbr(self, containerName):
        LXC_PATH = "/var/lib/lxc/"
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
        print ("first step end")
        with open(LXC_PATH + str(containerName) + '/config', "a") as myfile:
            myfile.write('\nlxc.network.link =')
            myfile.write(' ')
            myfile.write(str("br" + containerName))
            myfile.write('\n')
        print ("second step end")

    #Network creation of the container
    def clientContainerNetworking(self, containerName):



        portnumber = 10
        newIP = ""
        n = NothBoundLayer.Iport2.query.all()
        i = 0
        for nn in n:

            if (nn.bool == 0 and i == 0 and nn.port != 11):
                i = 1
                NothBoundLayer.store_ip(nn.id, i, containerName)
                portnumber = nn.port

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

        basiCmd = "sudo ovs-vsctl add-port OvsDc1 vethOvs" + str(containerName) + " -- set Interface vethOvs"+ str(containerName) + " ofport_request=" + str(portnumber)
        os.system(basiCmd)


    # setting the network in the destination node before migrating
    def clientContainerMigrationNetworking(self,containerName, destIP):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(destIP, username='root', password='iprotect')
        portnumber = 10

        n = NothBoundLayer.Iport2.query.all()
        for nn in n:
            if (nn.containerName == containerName):
                portnumber = nn.port




        basiCmd = "ip link add name veth" + str(containerName) + "Ovs type veth peer name vethOvs" + str(containerName)
        stdin, stdout, stderr = ssh.exec_command(basiCmd)

        basiCmd = "ip link set vethOvs" + str(containerName) + " up"
        stdin, stdout, stderr = ssh.exec_command(basiCmd)

        basiCmd = "ip link set veth" + str(containerName) + "Ovs up"
        stdin, stdout, stderr = ssh.exec_command(basiCmd)

        basiCmd = "brctl addbr br" + str(containerName)
        stdin, stdout, stderr = ssh.exec_command(basiCmd)

        basiCmd = "ifconfig br" + str(containerName) + " up"
        stdin, stdout, stderr = ssh.exec_command(basiCmd)

        basiCmd = "brctl addif br" + str(containerName) + " veth" + str(containerName) + "Ovs"
        stdin, stdout, stderr = ssh.exec_command(basiCmd)

        basiCmd2 = "sudo ovs-vsctl add-port OvsDc0 vethOvs" + str(containerName) + " -- set Interface vethOvs" + str(containerName) + " ofport_request=" + str(portnumber)
        stdin, stdout, stderr = ssh.exec_command(basiCmd2)








    # start the SDN network
    def startNetworking(self,containerName):
        n = NothBoundLayer.Iport2.query.all()
        for nn in n:
            if (nn.containerName == containerName):
                newIP = str(nn.ipaddress)
                self.set_ip(containerName,newIP)





    # delete the SDN network in the source node
    def deleteSourceNetworking(self, containerName, destIP):




        basiCmd = "brctl delif br" + str(containerName) + " veth" + str(containerName) + "Ovs"
        os.system(basiCmd)


        basiCmd = "ovs-vsctl del-port OvsDc1 vethOvs" + str(containerName)
        os.system(basiCmd)


        basiCmd = "ip link del dev veth" + str(containerName) + "Ovs"
        os.system(basiCmd)


        basiCmd = "ifconfig br" +str(containerName) + " down"
        os.system(basiCmd)


        basiCmd = "brctl delbr br" +str(containerName)
        os.system(basiCmd)


        n = NothBoundLayer.Iport2.query.all()
        for nn in n:
            if (nn.containerName == containerName):
                NothBoundLayer.destroy_ip(nn.id, 0)


    # delete the SDN network in the destination node
    def deleteDestinationNetworking(self, containerName, destIP):

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(destIP, username='root', password='iprotect')


        basiCmd = "brctl delif br" + str(containerName) + " veth" + str(containerName) + "Ovs"
        stdin, stdout, stderr = ssh.exec_command(basiCmd)


        basiCmd2 = "ovs-vsctl del-port OvsDc0 vethOvs" + str(containerName)
        stdin, stdout, stderr = ssh.exec_command(basiCmd2)


        basiCmd = "ip link del dev veth" + str(containerName) + "Ovs"
        stdin, stdout, stderr = ssh.exec_command(basiCmd)


        basiCmd = "ifconfig br" +str(containerName) + " down"
        stdin, stdout, stderr = ssh.exec_command(basiCmd)


        basiCmd = "brctl delbr br" +str(containerName)
        stdin, stdout, stderr = ssh.exec_command(basiCmd)


        n = NothBoundLayer.Iport2.query.all()
        for nn in n:
            if (nn.containerName == containerName):
                NothBoundLayer.destroy_ip(nn.id, 0)



    # delete the network in the source node after a success migration process
    def deleteNetworking2(self, containerName):




        basiCmd = "brctl delif br" + str(containerName) + " veth" + str(containerName) + "Ovs"
        os.system(basiCmd)


        basiCmd = "ovs-vsctl del-port OvsDc1 vethOvs" + str(containerName)
        os.system(basiCmd)


        basiCmd = "ip link del dev veth" + str(containerName) + "Ovs"
        os.system(basiCmd)


        basiCmd = "ifconfig br" +str(containerName) + " down"
        os.system(basiCmd)


        basiCmd = "brctl delbr br" +str(containerName)
        os.system(basiCmd)






    # set the ip of the SDN-enabled container
    def set_ip(self, containerName, newIP):
        LXC_PATH = "/var/lib/lxc/"
        i=0

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
                    myfile.write(str(newIP))
                    myfile.write('\n')
                    myfile.write('    netmask 255.255.255.0')











