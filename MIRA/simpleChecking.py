import subprocess
import os
import shutil
import sys
import paramiko
import time




class check():


    # verification if the container exist in the source node
    def nbrc(self, containerName):
        try:

            basiCmd = 'lxc-ls -f'
            result = subprocess.check_output(basiCmd, shell=True)
            myInfo = result.decode().split('\n')
            liste =[]
            for i in range(1,  int(len(myInfo)-1)):
                xx= myInfo[i].split(' ')
                if (xx[0] == str(containerName)):
                    return True
            return False

        except:
            print("unable to get number of containers")

    # verification if the container exist in the destination node
    def remoteMigrationCheck(self, containerName, destIP):
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
            liste = []
            for i in range(1, int(len(myInfo) - 1)):
                xx = myInfo[i].split(' ')
                if (xx[0] == str(containerName)):
                    return True
            return False


        except:
            print ("unable to execute remote checking")

