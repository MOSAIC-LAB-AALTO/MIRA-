import subprocess
import os
import sys
import time
import paramiko
import pycurl
from io import BytesIO
from urllib.parse import urlencode
import json


class test():

    def __init__(self):
        #self.x = migrateLXC.api()
        pass











    def basicONOSrest(self, strRquest, urlReq, post_data=None):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(pycurl.USERNAME, 'onos')
        c.setopt(pycurl.PASSWORD, 'rocks')
        c.setopt(pycurl.CUSTOMREQUEST, strRquest)
        c.setopt(c.URL, urlReq)
        if (post_data != None):
            c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json', 'Accept: application/json'])
            c.setopt(c.POST, 1)
            c.setopt(c.POSTFIELDS, post_data)
        else:
            c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])

        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        return buffer.getvalue()

    def getAllIntentsId(self, IP):
        strRquest = 'GET'
        urlReq = 'http://'+str(IP)+':8181/onos/v1/intents'
        body = self.basicONOSrest(strRquest, urlReq)
        resul = body.decode().split(sep='{')
        lstIds = []
        for i in range(2, len(resul)):
            temp = resul[i].split(sep=',')
            intenId = temp[1].split(sep=':')[1]
            lstIds.append(intenId.strip('"'))
        print('getAllIntents', lstIds)
        return lstIds




    def getAlllinks(self, IP):
        strRquest = 'GET'
        urlReq = 'http://'+str(IP)+':8181/onos/v1/links'
        body = self.basicONOSrest(strRquest, urlReq)

        resul = body.decode()
        f= json.loads(resul)
        link = f["links"]
        lsdevicePort =[{'portsrc':element['src']['port'], 'devicesrc':element['src']['device'], 'portdst':element['dst']['port'], 'devicedst':element['dst']['device']} for element in link]
        return lsdevicePort


    def getAlldevices(self, IP):
        strRquest = 'GET'
        urlReq = 'http://'+str(IP)+':8181/onos/v1/devices'
        body = self.basicONOSrest(strRquest, urlReq)
        resul = body.decode()
        f = json.loads(resul)
        devices = f["devices"]
        lsdeviceip = [{'device' : element['id'], 'ip_management' : element['annotations']['managementAddress']} for element in devices]
        return lsdeviceip

    def getAllhosts(self, IP):
        strRquest = 'GET'
        urlReq = 'http://'+str(IP)+':8181/onos/v1/hosts'
        body = self.basicONOSrest(strRquest, urlReq)
        resul = body.decode()
        f = json.loads(resul)
        hosts = f["hosts"]
        lshosts = [{'mac' : element['mac'], 'ip_container' : element['ipAddresses'], 'device' : element['location']['elementId'], 'port' : element['location']['port'] } for element in hosts]
        return lshosts


########################


    def getiP(self):

        basiCmd = 'lxc-ls -f'
        result = subprocess.check_output(basiCmd, shell=True)
        myInfo = result.decode().split('\n')
        liste = []
        for i in range(1, int(len(myInfo) - 1)):
            xx = myInfo[i].split(' ')
            basiCmd = 'lxc-info -n ' + str(xx[0])
            result = subprocess.check_output(basiCmd, shell=True)
            myInfo2 = result.decode().split('\n')
            containerStatus = myInfo2[1].replace(' ', '').split(':')[1]
            containerIP = myInfo2[3].replace(' ', '').split(':')[0]
            containerIP2 = myInfo2[4].replace(' ', '').split(':')[0]
            if (containerStatus == 'RUNNING' and containerIP == containerIP2):
                return (myInfo2[3].replace(' ', '').split(':')[1])



    def getSource(self, IP):

        containerIP = self.getiP()
        listofcontainer = self.getAllhosts(str(IP))
        ls =[]
        for i in range(0, int(len(listofcontainer))):
            ip = listofcontainer[i]['ip_container']
            port = listofcontainer[i]['port']
            if (ip[0] == containerIP):
                ls.append(ip[0])
                ls.append(port)
                return ls

        return "-1"



    def getDestination(self, IP):

        containerIP = self.getiP()
        listofcontainer = self.getAllhosts(str(IP))
        ls = []
        for i in range(0, int(len(listofcontainer))):
            ip = listofcontainer[i]['ip_container']
            port = listofcontainer[i]['port']
            if (ip[0] != containerIP):
                ls.append(ip[0])
                ls.append(port)
                return ls
        return "-1"

    def setInternaldevices(self, IP):

        ni.ifaddresses('ens38')
        ip = ni.ifaddresses('ens38')[ni.AF_INET][0]['addr']
        print (ip)
        listofdevice = self.getAlldevices(IP)
        print (listofdevice)
        print (len(listofdevice))
        listofinternaldevice = []
        for i in range(0, int(len(listofdevice))):
            deviceIP = listofdevice[i]['ip_management']
            if (deviceIP == ip):
                listofinternaldevice.append(listofdevice[i]['device'])
        print (listofinternaldevice)
        return listofinternaldevice




    def getdeviceclient(self, IP):
        temp = self.getSource(IP)
        listofcontainer = self.getAllhosts(IP)
        lsclient = []
        for i in range(0, int(len(listofcontainer))):
            ip = listofcontainer[i]['ip_container']
            if(ip[0] == temp[0]):
                device = listofcontainer[i]['device']
                port = listofcontainer[i]['port']
                lsclient.append(device)
                lsclient.append(port)

        return lsclient








    def getdeviceserver(self, IP):
        temp = self.getDestination(IP)
        listofcontainer = self.getAllhosts(IP)
        lsserver = []
        for i in range(0, int(len(listofcontainer))):
            ip = listofcontainer[i]['ip_container']
            if (ip[0] == temp[0]):
                device = listofcontainer[i]['device']
                port = listofcontainer[i]['port']
                lsserver.append(device)
                lsserver.append(port)
        return lsserver



    def getmigdevice(self, IP):
        src = self.getdeviceclient(IP)
        dst = self.getdeviceserver(IP)
        alldevice = self.getAlldevices(IP)
        migdevice =""

        for i in range (0, int(len(alldevice))):
            if (alldevice[i]['device'] != src[0] and alldevice[i]['device'] != dst[0]):
                migdevice= alldevice[i]['device']

        return migdevice




#######################

















