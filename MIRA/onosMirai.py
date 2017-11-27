import pycurl
from io import BytesIO
from urllib.parse import urlencode
import os
from time import sleep
import random
import onosCore

class migrationDemo():

    def __init__(self):
        self.onos = onosCore.test()

    # stop the RFW
    def stopFWD(self, IP):
        strRquest = 'DELETE'
        urlReq = 'http://' + str(IP) + ':8181/onos/v1/applications/org.onosproject.fwd/active'
        body = self.basicONOSrest(strRquest, urlReq)

    # connect to ONOS
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

    # Get all intents
    def getAllIntentsId(self, IP):
        strRquest = 'GET'
        urlReq = 'http://' + str(IP) + ':8181/onos/v1/intents'
        body = self.basicONOSrest(strRquest, urlReq)
        resul = body.decode().split(sep='{')
        lstIds = []
        for i in range(2, len(resul)):
            temp = resul[i].split(sep=',')
            intenId = temp[1].split(sep=':')[1]
            lstIds.append(intenId.strip('"'))

        print('getAllIntents', lstIds)
        return lstIds

    # delete all intents
    def delIntent(self, intentLst, IP):
        strRquest = 'DELETE'
        urlReqBase = 'http://' + str(IP) + ':8181/onos/v1/intents/org.onosproject.cli/'
        for i in range(len(intentLst)):
            urlReq = urlReqBase + intentLst[i]
            body = self.basicONOSrest(strRquest, urlReq)

    # parse intents
    def parseIntents(self, intentLst, IP):
        temp = []
        for x in intentLst:
            strRquest = 'GET'
            urlReq = 'http://' + str(IP) + ':8181/onos/v1/intents/org.onosproject.cli/'
            body = self.basicONOSrest(strRquest, urlReq + x)
            temp.append(body.decode())

        remove = []
        for y in temp:
            temp2 = y.split(sep=',')[10]
            if (temp2.split(sep=':')[1] == '21}]}'):
                temp3 = y.split(sep=',')[1]
                intenId = temp3.split(sep=':')[1]
                remove.append(intenId.strip('"'))
        return remove

    # Basic intent
    def createBasicIntentP2P(self, IP, ingressPointD, ingressPointP, egressPointD, egressPointP, priority):
        strRquest = 'POST'
        post_data1 = '{\"type": \"PointToPointIntent\", \"appId\": \"org.onosproject.cli\", \"priority\": ' + str(priority)
        post_data2 = post_data1 + ', \"ingressPoint\": {\"port\": \"' + str(ingressPointP)
        post_data3 = post_data2 + '\", "device": \"' + str(ingressPointD)
        post_data4 = post_data3 + '\"}, \"egressPoint\": {\"port\": \"' + str(egressPointP)
        post_data5 = post_data4 + '\", \"device\": \"' + str(egressPointD)
        post_data6 = post_data5 + '\"} }'
        urlReq = 'http://' + str(IP) + ':8181/onos/v1/intents'
        body = self.basicONOSrest(strRquest, urlReq, post_data6)

    # complexe intent
    def createIntentP2P(self, IP,ingressPointD, ingressPointP, egressPointD, egressPointP, priority, bandwidth,ethType, tcp, tcpPort):
        strRquest = 'POST'
        post_data1 = '{\"type\": \"PointToPointIntent\", \"appId\": \"org.onosproject.cli\", \"priority\":' + str(priority)
        post_data2 = post_data1 + ',\"ingressPoint\": {\"port\":\"' + str(ingressPointP)
        post_data3 = post_data2 + '\",\"device\":\"' + str(ingressPointD)
        post_data4 = post_data3 + '\"},\"egressPoint\": {\"port\":\"' + str(egressPointP)
        post_data5 = post_data4 + '\",\"device\":\"' + str(egressPointD)
        post_data6 = post_data5 + '\"},\"constraints\": [{\"bandwidth\":' + str(bandwidth)
        post_data7 = post_data6 + ',\"type\": \"BandwidthConstraint\"}],\"selector\": {\"criteria\": [{\"type\": \"ETH_TYPE\",\"ethType\": \"' + str(ethType)
        post_data8 = post_data7 + '\"},{\"type\": \"IP_PROTO\",\"protocol\": \"' + str(tcp)
        post_data9 = post_data8 + '\"},{\"type\": \"TCP_DST\",\"tcpPort\":' + str(tcpPort)
        post_data10 = post_data9 + '}]}}'
        urlReq = 'http://' + str(IP) + ':8181/onos/v1/intents'
        body = self.basicONOSrest(strRquest, urlReq, post_data10)

    # initial scenario
    def initialScenarioMIG(self, IP):

        deviceSource = self.onos.getdeviceclient(IP)
        deviceDestination = self.onos.getdeviceserver(IP)
        listOflinks = self.onos.getAlllinks(IP)
        for i in range(0, int(len(listOflinks) / 2)):
            devsrc = listOflinks[i]['devicesrc']
            devdst = listOflinks[i]['devicedst']

            if (deviceSource[0] == devsrc and deviceDestination[0] == devdst or deviceSource[0] == devdst and deviceDestination[0] == devsrc):
                #set the initial path

                portclient = self.onos.getSource(IP)
                portserver = self.onos.getDestination(IP)
                midport1 = listOflinks[i]['portsrc']
                midport2 = listOflinks[i]['portdst']
                myIntetsLst = self.getAllIntentsId(str(IP))
                self.delIntent(myIntetsLst, str(IP))

                self.delIntent(myIntetsLst, IP)
                self.createIntentP2P(str(IP), deviceSource[0], portclient[1], deviceSource[0], midport1, 100, 200, 2048, 6, 80)
                self.createIntentP2P(str(IP), deviceDestination[0], midport2, deviceDestination[0], portserver[1], 100, 200, 2048, 6, 80)
                self.createBasicIntentP2P(str(IP), deviceDestination[0], portserver[1], deviceDestination[0], midport2, 300)
                self.createBasicIntentP2P(str(IP), deviceSource[0], midport1, deviceSource[0], portclient[1], 300)



    def endMIG(self, IP):
        myIntetsLst = self.getAllIntentsId(str(IP))
        self.delIntent(myIntetsLst, str(IP))

    # end the first phase of migration
    def chaMIG1(self, IP):

        deviceSource = self.onos.getdeviceclient(IP)
        listOflinks = self.onos.getAlllinks(IP)
        devicemig = self.onos.getmigdevice(IP)
        for i in range(0, int(len(listOflinks) / 2)):
            devsrc = listOflinks[i]['devicesrc']
            devdst = listOflinks[i]['devicedst']

            if (deviceSource[0] == devsrc and devicemig == devdst or deviceSource[0] == devdst and devicemig == devsrc):


                portclient = self.onos.getSource(IP)
                portserver = self.onos.getDestination(IP)
                midport1 = listOflinks[i]['portsrc']
                midport2 = listOflinks[i]['portdst']
                myIntetsLst = self.getAllIntentsId(str(IP))
                self.delIntent(myIntetsLst, str(IP))

                self.createIntentP2P(str(IP), devicemig, midport2, devicemig, portserver[1], 100, 200, 2048, 6, 80)
                self.createBasicIntentP2P(str(IP), devicemig, portserver[1], devicemig, midport2, 300)
                self.createBasicIntentP2P(str(IP), deviceSource[0], midport1, deviceSource[0], portclient[1], 200)




    # end the second phase of migration
    def chaMIG2(self, IP):

        deviceSource = self.onos.getdeviceclient(IP)
        listOflinks = self.onos.getAlllinks(IP)
        devicemig = self.onos.getmigdevice(IP)
        for i in range(0, int(len(listOflinks) / 2)):
            devsrc = listOflinks[i]['devicesrc']
            devdst = listOflinks[i]['devicedst']

            if (deviceSource[0] == devsrc and devicemig == devdst or deviceSource[0] == devdst and devicemig == devsrc):
                portclient = self.onos.getSource(IP)
                portserver = self.onos.getDestination(IP)
                midport1 = listOflinks[i]['portsrc']
                midport2 = listOflinks[i]['portdst']

                self.createIntentP2P(str(IP), deviceSource[0], portclient[1], deviceSource[0], midport1, 100, 200, 2048, 6, 80)



