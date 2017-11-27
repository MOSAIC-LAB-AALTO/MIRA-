import sys
import os
import paramiko
import subprocess
import shutil



class dstCtrl():




    ###########################################################################
    #																		  #
    #	                 Linux Container Resources Part			              #
    #            															  #
    ###########################################################################



    # information about container's CPU
    def getcpu(self, containerName, destIP):
        try:
            print("Getting cpu information")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(destIP, username='root', password='iprotect')
            basiCmd = 'lxc-cgroup -n ' + str(containerName) + ' cpuset.cpus'
            stdin, stdout, stderr = ssh.exec_command(basiCmd)
            result = stdout.read()
            stdin.flush()
            ssh.close()
            myInfo = result.decode().split('\n')
            numberCpu = myInfo[0].split('-')
            numberCpu2 = str((int(numberCpu[1]) - int(numberCpu[0])) + 1)
            return int(numberCpu2)
        except:
            print("unable to GET CPU information")

    # more efficient information about container's CPU
    def getcpu2(self, containerName, destIP):
        try:

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(destIP, username='root', password='iprotect')

            cmd = ' cat /var/lib/lxc/' + containerName + '/config'
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read()
            stdin.flush()
            ssh.close()

            contenu = result.decode().split('\n')
            for line in contenu:
                if "lxc.cgroup.cpuset.cpus" in line:
                    print(line)
                    myInfo = line.decode().split(' = ')
                    if '-' in myInfo[1]:
                        numberCpu = myInfo[1].split('-')
                        numberCpu2 = str((int(numberCpu[1]) - int(numberCpu[0])) + 1)
                        return int(numberCpu2)
                    else:
                        return 1
        except:
            print("unable to GET CPU information")




    # information about container's Memory
    def getmem(self, containerName, destIP):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(destIP, username='root', password='iprotect')
            print("Getting Memory information")
            basiCmd = 'cat /sys/fs/cgroup/memory/lxc/' + containerName + '/memory.limit_in_bytes'
            stdin, stdout, stderr = ssh.exec_command(basiCmd)
            result = stdout.read()
            stdin.flush()
            ssh.close()
            myInfo = result.decode().split('\n')
            return (int(myInfo[0])/1024/1024)
        except:
            print("unable to GET Memory information")

    # more efficient information about container's Memory
    def getmem2(self, containerName, destIP):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(destIP, username='root', password='iprotect')

            print("Getting Memory information")

            cmd = ' cat /var/lib/lxc/' + containerName + '/config'
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read()
            stdin.flush()
            ssh.close()

            contenu = result.decode().split('\n')
            for line in contenu:
                if "lxc.cgroup.memory.limit_in_bytes" in line:
                    print(line)
                    myInfo = line.split(' = ')
                    if 'M' in myInfo[1]:
                        temp = myInfo[1].split('M')
                        print(temp[0])
                        return int(temp[0])
                    else:
                        temp = myInfo[1].split('G')
                        print(int(temp[0]) * 1024)
                        return int(temp[0]) * 1024
        except:
            print("unable to GET Memory information")



    # information about container's Size
    def getsize(self, containerName, destIP):
        try:
            print("Getting the size of the container")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(destIP, username='root', password='iprotect')
            basiCmd = 'du -sh /var/lib/lxc/' + containerName + '/'
            stdin, stdout, stderr = ssh.exec_command(basiCmd)
            result = stdout.read()
            stdin.flush()
            ssh.close()
            myInfo = result.decode().split('\t')

            for i in range(1, int(len(myInfo[0]) + 1)):
                if (myInfo[0][i - 1] == 'M'):
                    res = myInfo[0].split('M')
                    return int(res[0])
                elif (myInfo[0][i - 1] == 'G'):
                    res = myInfo[0].split('G')
                    firstNumber = float(res[0])
                    secondNumber = float(1000.0)
                    answer = (firstNumber * secondNumber)
                    return answer

        except:
            print("unable to GET the size of the container")




    # liste of all the containers
    def nbrc(self, destIP):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(destIP, username='root', password='iprotect')
            basiCmd = 'lxc-ls -f'
            stdin, stdout, stderr = ssh.exec_command(basiCmd)
            result = stdout.read()
            stdin.flush()
            ssh.close()
            myInfo = result.decode().split('\n')
            liste =[]
            for i in range(1,  int(len(myInfo)-1)):
                xx= myInfo[i].split(' ')
                liste.append(xx[0])

            for i in range(1, int(len(myInfo)-1)):
                print(liste[i-1])

            return liste

        except:
            print("unable to get number of containers")


    ###########################################################################
    #																		  #
    #	                 Virtual Machine Resources Part			              #
    #            															  #
    ###########################################################################

    # Getting the Disk of the VM
    def getvmdisk(self, destIP):
        try:

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(destIP, username='root', password='iprotect')
            runCMD = 'df -H /'
            stdin, stdout, stderr = ssh.exec_command(runCMD)
            result = stdout.read()
            stdin.flush()
            ssh.close()
            myInfo = result.decode().split('\n')
            vmStatus = myInfo[1].split()[0:6]
            for i in range(1,  int(len(vmStatus[0])+1)):
                if (vmStatus[3][i-1] == 'M'):
                    res= vmStatus[3].split('M')
                    return res[0]
                elif(vmStatus[3][i-1] == 'G'):
                    res = vmStatus[3].split('G')
                    firstNumber = float(res[0].replace(',', '.'))
                    secondNumber = float(1000.0)
                    answer = (firstNumber * secondNumber)
                    return answer
        except:
            print("unable to get disk information from our VM")

    # Getting the Memory of the VM
    def getvmmem(self, destIP):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(destIP, username='root', password='iprotect')
            basiCmd = 'vmstat -s'
            stdin, stdout, stderr = ssh.exec_command(basiCmd)
            result = stdout.read()
            stdin.flush()
            ssh.close()
            myInfo = result.decode().split('\n')
            free_memory = myInfo[4].split()[0:3]
            return int(int(free_memory[0])/1024)
        except:
            print("unable to get memory information from our VM ")

    # Getting the CPU of the VM
    def getvmcpu(self, destIP):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(destIP, username='root', password='iprotect')
            basiCmd = 'nproc'
            stdin, stdout, stderr = ssh.exec_command(basiCmd)
            result = stdout.read()
            stdin.flush()
            ssh.close()
            return int(result)
        except:
            print("unable to get cpu information from our VM")