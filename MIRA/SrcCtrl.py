import sys
import os
import paramiko
import subprocess



class srcCtrl():



    # information about container's CPU
    def getcpu(self, containerName):
        try:
            print("Getting cpu information")
            basiCmd = 'lxc-cgroup -n ' + str(containerName) + ' cpuset.cpus'
            result = subprocess.check_output(basiCmd, shell=True)
            myInfo = result.decode().split('\n')
            #to correct
            if '-' in myInfo[0]:
                numberCpu = myInfo[0].split('-')
                numberCpu2 = str((int(numberCpu[1])-int(numberCpu[0]))+1)
                return numberCpu2
            else:
                return 1
        except:
            print("unable to GET CPU information")


    # information about container's Memory
    def getmem(self, containerName):
        try:
            print("Getting Memory information")
            basiCmd = 'cat /sys/fs/cgroup/memory/lxc/' + str(containerName) + '/memory.limit_in_bytes'
            result = subprocess.check_output(basiCmd, shell=True)
            myInfo = result.decode().split('\n')
            return int(int(myInfo[0])/1024/1024)
        except:
            print("unable to GET Memory information")



    #information about container's Size
    def getsize(self, containerName):
        try:
            print("Getting the size of the container")
            basiCmd = 'du -sh /var/lib/lxc/' + str(containerName) + '/'
            result = subprocess.check_output(basiCmd, shell=True)
            myInfo = result.decode().split('\t')

            for i in range(1,  int(len(myInfo[0])+1)):
                if (myInfo[0][i-1] == 'M'):
                    res= myInfo[0].split('M')
                    return res[0]
                elif(myInfo[0][i-1] == 'G'):
                    res = myInfo[0].split('G')
                    firstNumber = float(res[0].replace(',', '.'))
                    secondNumber = float(1000.0)
                    answer = (firstNumber * secondNumber)
                    return answer

        except:
            print("unable to GET the size of the container")


