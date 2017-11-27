import subprocess
import os
import shutil
import sys
import paramiko
import time




class monitor():

    # Getting the running container
    def containerList(self):
        try:

            basiCmd = 'lxc-ls -f'
            result = subprocess.check_output(basiCmd, shell=True)
            myInfo = result.decode().split('\n')
            liste =[]
            for i in range(1,  int(len(myInfo)-1)):
                xx = myInfo[i].split(' ')
                basiCmd = 'lxc-info -n ' + str(xx[0])
                result = subprocess.check_output(basiCmd, shell=True)
                myInfo2 = result.decode().split('\n')
                containerStatus = myInfo2[1].replace(' ', '').split(':')[1]
                if (containerStatus == 'RUNNING'):
                    liste.append(xx[0])

            return liste




        except:
            print("unable to get the list of containers")

    # Get the live CPU consumption
    def getLiveCpu(self, containerName):
        # /sys/fs/cgroup/memory/lxc/
        with open('/sys/fs/cgroup/cpuacct/lxc/%s/cpuacct.usage' % (containerName,), 'r') as f:
            cpu_usage = int(f.readline())

        return (cpu_usage/10**9)

    # Get the live Memory consumption
    def getLiveMem(self, containerName):
        # with open('/sys/fs/cgroup/memory/lxc/%s/memory.stat' % (containerName,), 'r') as f:
        s = 0
        i = 0
        for line in open('/sys/fs/cgroup/memory/lxc/%s/memory.stat' % (containerName,), 'r'):
            if "total_cache" in line:
                x = line.split(' ')
                s = s + int(x[1])
            if "total_rss" in line:
                if (i == 0):
                    x = line.split(' ')
                    s = s + int(x[1])
                    i = 1

        return (s/1024)/1024