
import sys
import os
import paramiko
import subprocess
import fileinput




# this class implement a customized creation of container tech
class cCreate():



    # customized CPU
    def modcpu(self, containerName, val):
        LXC_PATH = "/var/lib/lxc/"
        i=0

        for line in open(LXC_PATH + str(containerName) + '/config', "r"):
            if "lxc.cgroup.cpuset.cpus" in line:
                with open(LXC_PATH + str(containerName) + '/config', "r") as input:
                    with open(LXC_PATH + str(containerName) + '/config2', "wb") as output:
                        for line2 in input:
                            if line2 != line:
                                output.write(line2)

                basiCmd = 'rm ' + LXC_PATH + str(containerName) + '/config'
                os.system(basiCmd)
                basiCmd = 'mv ' + LXC_PATH + str(containerName) + '/config2 ' + LXC_PATH + str(containerName) + '/config'
                os.system(basiCmd)
                if (val == "1"):
                    with open(LXC_PATH + str(containerName) + '/config', "a") as myfile:
                        myfile.write('\nlxc.cgroup.cpuset.cpus =')
                        myfile.write(' ')
                        myfile.write(str(int(val)-1))
                        myfile.write('\n')
                else:
                    with open(LXC_PATH + str(containerName) + '/config', "a") as myfile:
                        myfile.write('\nlxc.cgroup.cpuset.cpus =')
                        myfile.write(' 0-')
                        myfile.write(str(int(val)-1))
                        myfile.write('\n')




                i=1
        if (i == 0):
            if (val == "1"):
                with open(LXC_PATH + str(containerName) + '/config', "a") as myfile:
                    myfile.write('\nlxc.cgroup.cpuset.cpus =')
                    myfile.write(' ')
                    myfile.write(str(int(val) - 1))
                    myfile.write('\n')
            else:
                with open(LXC_PATH + str(containerName) + '/config', "a") as myfile:
                    myfile.write('\nlxc.cgroup.cpuset.cpus =')
                    myfile.write(' 0-')
                    myfile.write(str(int(val) - 1))
                    myfile.write('\n')


    # customized Memory
    def modram(self, containerName, val):
        LXC_PATH = "/var/lib/lxc/"
        i = 0

        for line in open(LXC_PATH + str(containerName) + '/config', "r"):
            if "lxc.cgroup.memory.limit_in_bytes" in line:
                with open(LXC_PATH + str(containerName) + '/config', "r") as input:
                    with open(LXC_PATH + str(containerName) + '/config2', "wb") as output:
                        for line2 in input:
                            if line2 != line:
                                output.write(line2)

                basiCmd = 'rm ' + LXC_PATH + str(containerName) + '/config'
                os.system(basiCmd)
                basiCmd = 'mv ' + LXC_PATH + str(containerName) + '/config2 ' + LXC_PATH + str(containerName) + '/config'
                os.system(basiCmd)
                with open(LXC_PATH + str(containerName) + '/config', "a") as myfile:
                    myfile.write('\nlxc.cgroup.memory.limit_in_bytes =')
                    myfile.write(' ')
                    myfile.write(val)
                    myfile.write('\n')


                i =1
        if (i == 0):
            with open(LXC_PATH + str(containerName) + '/config', "a") as myfile:
                myfile.write('\nlxc.cgroup.memory.limit_in_bytes =')
                myfile.write(' ')
                myfile.write(val)
                myfile.write('\n')