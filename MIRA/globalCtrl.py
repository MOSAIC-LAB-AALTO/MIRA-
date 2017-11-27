import os
import paramiko
import paramiko
import subprocess
import sys

import DstCtrl
import SrcCtrl
import migrateLXC


class Ctrl():

    def __init__(self):
        self.x = SrcCtrl.srcCtrl()
        self.y = DstCtrl.dstCtrl()
        self.z = migrateLXC.api()
        self.CPU = 0
        self.RAM = 0
        self.containerDISK = 0.0



    # Getting the container's information from the source node
    def sourceChecking(self, containerName):

        try:
            print("---CPU---")
            self.CPU = self.x.getcpu(containerName)
            print(self.CPU)
        except:
            print("failed ---CPU---")
        try:
            print("---RAM---")
            self.RAM = self.x.getmem(containerName)
            print(self.RAM)
        except:
            print("failed ---RAM---")
        try:
            print("---DISK---")
            self.containerDISK = self.x.getsize(containerName)
            print(self.containerDISK)
        except:
            print("failed ---DISK---")


    # Verification in the target node before migration
    def destinationChecking(self, containerName, destIP):

        #semi-pessimiste
        #comparr to the current available size of the VM
        if (float(self.containerDISK) < float(self.y.getvmdisk(destIP))):
            print("good to continue")
            liste = self.y.nbrc(destIP)

            vmcpu = self.y.getvmcpu(destIP)
            vmmem = self.y.getvmmem(destIP)

            for i in range(1,  int(len(liste)+1)):

                resultInfo = self.z.remoteInfo(liste[i-1], destIP)
                if (resultInfo == 'STOPPED'):
                    print("container is stopped wth")

                if (resultInfo == 'RUNNING'):
                    vmcpu = vmcpu - self.y.getcpu2(liste[i-1], destIP)
                    vmmem = vmmem - self.y.getmem2(liste[i-1], destIP)

            print(int(vmmem))
            print(int(vmcpu))
            print(int(self.RAM))
            print(int(self.CPU))
            if int(vmmem) >= int(self.RAM) and int(vmcpu) >= int(self.CPU):
                print("good to create")
                return True
            else:
                print("not enough resources")
                return False


        else:
            print("big issue")
            return False

    # Verification in the target node before migration
    def destinationChecking2(self, containerName, destIP):
        #pessimiste
        if (float(self.containerDISK) < float(self.y.getvmdisk(destIP))):
            print("good to continue")
            liste = self.y.nbrc(destIP)

            vmcpu = self.y.getvmcpu(destIP)
            vmmem = self.y.getvmmem(destIP)

            for i in range(1,  int(len(liste)+1)):

                resultInfo = self.z.remoteInfo(liste[i-1], destIP)
                if (resultInfo == 'STOPPED'):
                    print("container is stopped wth")
                    #i should add a way to verify even when it's shutdown

                if (resultInfo == 'RUNNING'):
                    vmcpu = vmcpu - self.y.getcpu(liste[i-1], destIP)
                    vmmem = vmmem - self.y.getmem(liste[i-1], destIP)

            print(int(vmmem))
            print(int(vmcpu))
            print(int(self.RAM))
            print(int(self.CPU))
            if int(vmmem) >= int(self.RAM) and int(vmcpu) >= int(self.CPU):
                print("good to create")
                return True
            else:
                print("not enough resources")
                return False


        else:
            print("big issue not enough disk resources")
            return False





