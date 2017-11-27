import subprocess
import os
import shutil
import sys
import paramiko
import time
import logging
import customCreate
import createSDN
import onosMirai

NOK = -1
OK = 1

my_logger = logging.getLogger('controLog')


class api:
    # -*-coding:utf-8 -*
    # define LXC path
    def __init__(self, LXC_Path='/var/lib/lxc/'):
        self.driveONOS2 = onosMirai.migrationDemo()
        self.LXC_PATH = LXC_Path
        self.cCreate = customCreate.cCreate()
        self.sdn = createSDN.createNetwork()


    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # get general information

    def info(self, containerName):
        try:
            basiCmd = 'lxc-info -n ' + str(containerName)
            result = subprocess.check_output(basiCmd, shell=True)
            return result
        except:

            print("unable to get specific information about the container")
            return NOK
    # def info() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # specific remote info
    def remoteInfo(self, containerName, destIP):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(destIP, username='root', password='iprotect')
        basiCmd = 'lxc-info -n ' + str(containerName)
        stdin, stdout, stderr = ssh.exec_command(basiCmd)
        result = stdout.read()
        stdin.flush()
        ssh.close()
        myInfo = result.decode().split('\n')
        containerStatus = myInfo[1].replace(' ', '').split(':')[1]
        return containerStatus
    # def remoteInfo() - END



    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    #get information from a choosen container
    def detailedInfo(self,containerName):
        try:
            basiCmd = 'lxc-info -n ' + str(containerName)
            result = subprocess.check_output(basiCmd, shell=True)
            myInfo = result.decode().split('\n')
            containerStatus = myInfo[1].replace(' ', '').split(':')[1]
            if containerStatus == 'STOPPED':
                cname = myInfo[0].replace(' ','').split(':')[1]
                results = str(OK) + '#' + cname + '#' + containerStatus
                return results
            else:
                cname = myInfo[0].replace(' ', '').split(':')[1]
                results = str(OK) + '#' + cname + '#' + containerStatus
                strContainerPID = myInfo[2].replace(' ', '').split(':')[1]
                results = results + '#' + strContainerPID
                strContainerIP = myInfo[3].replace(' ', '').split(':')[1]
                results = results + '#' + strContainerIP
                CPU_USE = myInfo[4].replace(' ', '').split(':')[1]
                results = results + '#' + CPU_USE
                BlkIO_use = myInfo[5].replace(' ', '').split(':')[1]
                results = results + '#' + BlkIO_use
                Memory_use = myInfo[6].replace(' ', '').split(':')[1]
                results = results + '#' + Memory_use
                Link = myInfo[8].replace(' ', '').split(':')[1]
                results = results + '#' + Link
                TX_bytes = myInfo[9].replace(' ', '').split(':')[1]
                results = results + '#' + TX_bytes
                RX_bytes = myInfo[10].replace(' ', '').split(':')[1]
                results = results + '#' + RX_bytes
                return results
        except:

            print("unable to get specific information about the container")
            return NOK
    # def detailedInfo() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # get the PID of our container
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

    # def getPIDstr() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # get the network interface information
    def getEth0(self, containerName):
        try:
            resultInfo = self.info(containerName)
            myInfo = resultInfo.decode().split('\n')
            containerStatus = myInfo[1].replace(' ', '').split(':')[1]

            # Must implement remote verify
            if (containerStatus == 'STOPPED'):
                # self.copy(containerName, destIP, migType)
                return NOK
            if (containerStatus == 'RUNNING'):
                myEth0 = myInfo[7].replace(' ', '').split(':')[1]
                return str(myEth0)
        except:
            # def info() - END
            print("unable to get specific information about the container")
            return None

    # getEth0() - end

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # get the two network interfaces
    def getEth0_2IP(self, containerName):
        try:
            resultInfo = self.info(containerName)
            myInfo = resultInfo.decode().split('\n')
            containerStatus = myInfo[1].replace(' ', '').split(':')[1]

            # Must implement remote verify
            if (containerStatus == 'STOPPED'):
                # self.copy(containerName, destIP, migType)
                return NOK
            if (containerStatus == 'RUNNING'):
                myEth0 = myInfo[9].replace(' ', '').split(':')[1]
                return str(myEth0)
        except:
            # def info() - END
            print("unable to get specific information about the container")
            return None

    # getEth0_2IP() - end

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # create container
    def create(self, containerName, cpu, ram):
        try:
            print("container creation :")
            basiCmd = 'lxc-create -t ubuntu -n ' + str(containerName) + ' -- -r trusty -a amd64'
            os.system(basiCmd)
            with open(self.LXC_PATH + str(containerName) + '/config', "a") as myfile:
                myfile.write('\n# hax for criu\n')
                myfile.write('lxc.console = none\n')
                myfile.write('lxc.tty = 0\n')
                myfile.write('lxc.cgroup.devices.deny = c 5:1 rwm\n')
            self.cCreate.modcpu(containerName, cpu)
            self.cCreate.modram(containerName, ram)
            self.sdn.modconfigbr(containerName)
            self.sdn.clientContainerNetworking(containerName)
            self.sdn.startNetworking(containerName)
            return OK
        except:
            print("unable to create to create the container")
            return NOK

    # def create() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # create a demo version of the code using nginx server and SDN technologies
    def createnginx(self, containerName, cpu, ram, IPSDN):
        try:
            print("container creation :")
            basiCmd = 'lxc-copy -n nginxBKserver -N ' + containerName
            os.system(basiCmd)
            time.sleep(2)
            with open(self.LXC_PATH + str(containerName) + '/config', "a") as myfile:
                myfile.write('\n# hax for criu\n')
                myfile.write('lxc.console = none\n')
                myfile.write('lxc.tty = 0\n')
                myfile.write('lxc.cgroup.devices.deny = c 5:1 rwm\n')
            self.cCreate.modcpu(containerName, cpu)
            self.cCreate.modram(containerName, ram)
            self.sdn.modconfigbr(containerName)
            self.sdn.clientContainerNetworking(containerName)
            self.sdn.startNetworking(containerName)
            time.sleep(5)
            self.start(containerName)
            time.sleep(2)
            self.driveONOS2.initialScenarioMIG(IPSDN)
            return OK
        except:
            print("unable to create to create the container")
            return NOK
        # def createnginx() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # clone the container
    def clone(self, baseContainerName, newContainerName):
        try:
            basiCmd = 'lxc-copy -n ' + baseContainerName + ' -N' + newContainerName
            os.system(basiCmd)
            return OK
        except Exception as exception:
            my_logger.critical('ERROR: migrateLXC.API.clone():' + str(exception) + '\n')
            return NOK

    # def clone() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # delete simple container
    def delete(self, containerName):
        try:
            basiCmd = 'lxc-destroy -n ' + str(containerName) + ' --force'
            os.system(basiCmd)
            return OK
        except:
            return NOK

    # def delete() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################



    # delete SDN-based container during the migration

    def delete2(self, containerName):
        try:
            basiCmd = 'lxc-destroy -n ' + str(containerName) + ' --force'
            os.system(basiCmd)
            self.sdn.deleteNetworking2(containerName)
            return OK
        except:
            return NOK

         # def delete() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # start the container
    def start(self, containerName):
        try:
            print("container starting :")
            basiCmd = 'lxc-start -n ' + str(containerName)
            os.system(basiCmd)
            return OK
        except Exception as exception:
            my_logger.critical('ERROR: migrateLXC.API.start():' + str(exception) + '\n')
            return NOK

    # def start() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # stop the container
    def stop(self, containerName):
        try:
            print("container stopping :")
            basiCmd = 'sudo lxc-stop -n ' + str(containerName)
            os.system(basiCmd)
            return OK
        except:
            print("unable to stop the container")
            return NOK

    # def stop() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # get general information about all containers
    def geninfo(self):
        try:
            print("get general informations about all containers")
            basiCmd = 'sudo lxc-ls'
            os.system(basiCmd)
            return OK
        except:
            print("unable to get generel informations")
            return NOK

    # def getinfo() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # just show a message
    def cleanUPFailMig(self):
        print('TODO: remove rsync and cleanUP')

    # def cleanUPFailMig() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # delete the existinig files
    def rmDir(self, containerName, destIP):
        try:
            ckptPath = self.LXC_PATH + str(containerName) + '/checkpoint'
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(destIP, username='root', password='iprotect')
            runCMD = 'rm  -rf ' + ckptPath + '/*'
            stdin, stdout, stderr = ssh.exec_command(runCMD)
            ssh.close()
            result = subprocess.check_output(runCMD, shell=True)
            return OK
        except Exception as exception:
            return NOK

    # def rmDir() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # mount the folder in order to contain the memory
    def mountCkpt(self, containerName, destIP):
        # TODO: CREATE IF NOT EXISTS
        if not os.path.exists(self.LXC_PATH + str(containerName) + '/checkpoint'):
            os.makedirs(self.LXC_PATH + str(containerName) + '/checkpoint')

        try:
            ckptPath = self.LXC_PATH + str(containerName) + '/checkpoint/'
            mountCMD = 'mount -t tmpfs -o size=1500M,mode=0777 tmpfs ' + ckptPath
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(destIP, username='root', password='iprotect')
            mkdirCMD1 = 'mkdir ' + self.LXC_PATH + str(containerName)
            mkdirCMD2 = 'mkdir ' + ckptPath
            stdin, stdout, stderr = ssh.exec_command(mkdirCMD1)
            stdin, stdout, stderr = ssh.exec_command(mkdirCMD2)
            result = subprocess.check_output(mountCMD, shell=True)
            stdin, stdout, stderr = ssh.exec_command(mountCMD)
            ssh.close()
        except:
            self.cleanUPFailMig()
            return NOK

    # def mountCkpt() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # clean methode
    def last(self, containerName, destIP):

        waitCMD = 'lxc-wait -n ' + str(containerName) + ' -s RUNNING'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(destIP, username='root', password='iprotect')
        stdin, stdout, stderr = ssh.exec_command(waitCMD)
        time.sleep(5)
        umntCMD = '/root/umount.sh ' + containerName
        result = subprocess.check_output(umntCMD, shell=True)
        stdin, stdout, stderr = ssh.exec_command(umntCMD)
        ssh.close()

    # def last() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # restore function
    def restore(self, containerName, destIP, numIntera):
        restoreCMD = 'lxc-checkpoint -r -n ' + str(containerName)
        restoreCMD = restoreCMD + ' -D /var/lib/lxc/'
        restoreCMD = restoreCMD + str(containerName) + '/checkpoint/'
        restoreCMD = restoreCMD + str(numIntera) + '/ -vvvvv'
        print(restoreCMD)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(destIP, username='root', password='iprotect')
        stdin, stdout, stderr = ssh.exec_command(restoreCMD)
        ssh.close()

    # def restore() -END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # last clean up
    def cleaning(self, containerName, destIP):
        runCMD = 'rm  -rf /var/lib/lxc/' + containerName + '/checkpoint/3/*'
        result3 = subprocess.check_output(runCMD, shell=True)

    # def cleaning() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # iterative migration
    def dump(self, containerName, destIP, numIntera):
        general_args = ""
        try:
            resultInfo = self.info(containerName)
            myInfo = resultInfo.decode().split('\n')
            containerStatus = myInfo[1].replace(' ', '').split(':')[1]

            # Must implement remote verify
            if (containerStatus == 'STOPPED'):
                print("container is stopped")
                return
            if (containerStatus == 'RUNNING'):
                strContainerPID = myInfo[2].replace(' ', '').split(':')[1]
                print(strContainerPID)
                self.rmDir(containerName, destIP)
                synDirCmd = 'rsync -aAXHltzh --numeric-ids --devices --rsync-path='
                synDirCmd = synDirCmd + '\"sudo rsync\" ' + self.LXC_PATH + containerName
                synDirCmd = synDirCmd + ' root@' + str(destIP) + ':' + self.LXC_PATH
                result = subprocess.check_output(synDirCmd, shell=True)
                rst = self.mountCkpt(containerName, destIP)
                general_args = '--tcp-established --cgroup-dump-controller c1'
                general_args = general_args + ' --file-locks'
                general_args = general_args + ' --link-remap --force-irmap'
                general_args = general_args + ' --manage-cgroups'
                general_args = general_args + ' --ext-mount-map auto'
                general_args = general_args + ' --enable-external-sharing'
                general_args = general_args + ' --enable-external-masters'
                general_args = general_args + ' --enable-fs hugetlbfs --enable-fs tracefs'
                general_args = general_args + ' -vvvvvv'
                general_args = general_args + ' -t ' + str(strContainerPID)

                #############################################
                # print (general_args)

                #############################################
                fin = 0
                print("ready to be in dump phase")
                # i=1
                for i in range(1, int(numIntera) + 1):
                    # print("iteration :" + i)
                    print(str(int(numIntera) - 1))
                    ckptPath = self.LXC_PATH + str(containerName) + '/checkpoint/' + str(i)
                    mkdirCMD1 = 'mkdir ' + ckptPath
                    result = subprocess.check_output(mkdirCMD1, shell=True)

                    if (i == 1):
                        # First snapshot -- no parent, kill afterwards
                        if (int(numIntera) == 1):
                            action = 'dump'
                            args = '-s --track-mem'
                        else:
                            action = 'pre-dump'
                            args = '--track-mem --leave-running'

                    elif (i == int(numIntera)):
                        # Last snapshot -- has parent, kill afterwards
                        args = '--prev-images-dir=../' + str(int(numIntera) - 1) + '/ --track-mem --leave-stopped'
                        action = 'dump'
                        fin = 1
                    else:
                        # Other snapshots -- have parent, keep running
                        args = '--prev-images-dir=../' + str(i - 1) + '/ --track-mem --leave-running'
                        action = 'pre-dump'

                    criuCMD = 'criu ' + action + ' -D ' + ckptPath + ' -o ' + ckptPath + '/' + action + '.log ' + general_args + ' ' + args
                    print (criuCMD)
                    result1 = subprocess.check_output(criuCMD, shell=True)
                    if (i == int(numIntera)):
                        print("dump :" + str(i))
                    else:
                        print("pre-dump :" + str(i))
                    synDirCmd1 = 'rsync -aAXHltzh --numeric-ids --devices --rsync-path='
                    synDirCmd1 = synDirCmd1 + '\"sudo rsync\" ' + ckptPath + '/'
                    synDirCmd1 = synDirCmd1 + ' root@' + str(destIP) + ':' + ckptPath + '/'
                    result2 = subprocess.check_output(synDirCmd1, shell=True)
        except:
            print("unable to performe dump")
            print("let's try a new one")
            # special method to solve last dump problem
            j = 1
            while (j <= 3):
                try:
                    # do cleaning
                    self.cleaning(containerName, destIP)
                    # redo dump
                    ckptPath = self.LXC_PATH + str(containerName) + '/checkpoint/' + str(int(numIntera))
                    args = '--prev-images-dir=../' + str(int(numIntera) - 1) + '/ --track-mem --leave-stopped'
                    action = 'dump'
                    print(general_args)
                    criuCMD = 'criu ' + action + ' -D ' + ckptPath + ' -o ' + ckptPath + '/' + action + '.log ' + general_args + ' ' + args
                    synDirCmd1 = 'rsync -aAXHltzh --numeric-ids --devices --rsync-path='
                    synDirCmd1 = synDirCmd1 + '\"sudo rsync\" ' + ckptPath + '/'
                    synDirCmd1 = synDirCmd1 + ' root@' + str(destIP) + ':' + ckptPath + '/'
                    result2 = subprocess.check_output(synDirCmd1, shell=True)
                    j = 5
                except:
                    j += 1

            if (j <= 4):
                print("failed to dump")
            else:
                print("successful dump")

    # def dump() -END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################

    # migration implementation
    def migrate(self, containerName, destIP, numIntera, IPSDN):
        try:
            print("setting the sdn network in the target side")
            self.sdn.clientContainerMigrationNetworking(containerName, destIP)
        except:
            print("unable to create the sdn network")

        try:
            print("start dumpping")
            self.dump(containerName, destIP, numIntera)

        except:
            print("unable to performe dump")
            return NOK
        try:
            print("onos part ......")
            self.driveONOS2.chaMIG1(IPSDN)
            self.driveONOS2.chaMIG2(IPSDN)
        except:
            print("onos broke -_-")

        try:
            print("start restore")
            self.restore(containerName, destIP, numIntera)
        except:
            print("unable to do restore")
            return NOK
        try:
            self.last(containerName, destIP)
        except:
            print("unable to do last")
            return NOK
        try:
            self.delete2(containerName)
        except:
            print("unable to do destroy")
            return NOK
        return OK

            # def migrate() - END

    ###########################################################################
    #																		  #
    #																		  #
    #            															  #
    ###########################################################################