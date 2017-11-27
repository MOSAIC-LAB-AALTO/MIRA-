from flask import Flask, request, jsonify, json, render_template, Response
import producer
from sqlalchemy import create_engine, MetaData, Table
from flask.ext.sqlalchemy import SQLAlchemy
import time
import simpleChecking
import main
import monitoring
import onosCore
from uuid import uuid4

#database name
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///MIRAI4.db"
db = SQLAlchemy(app)


#multiprocessing call, checking module call, monitoring module call
t =  producer.producer()
checking = simpleChecking.check()
truechecking = main.mainclass()
monitor = monitoring.monitor()
clear = onosCore.test()
token = 1
from sqlalchemy import Column, Integer, String

#database class
class Mirai4(db.Model):
    #table name & components (creation)
    __tablename__ = 'mirai4'
    id = db.Column(Integer, primary_key=True)
    containerName = db.Column(String(120))
    result = db.Column(String(50) )
    code = db.Column(String(120))
    newcontainerName = db.Column(String(120))
    token = db.Column(String(120))

    #initialization of one raw in the database
    def __init__(self,containerName, code=None, result=None, newcontainerName=None, token=None):
        self.containerName = containerName
        self.result = result
        self.code = code
        self.newcontainerName = newcontainerName
        self.token = token

    def __repr__(self):
        return '<Request %r>' % (self.result)

#monitoring database call
class Miraimonitor(db.Model):
    # table name & components (creation)
    __tablename__ = 'monitoring'
    id = db.Column(Integer, primary_key=True)
    containerName = db.Column(String(120))
    realtime = db.Column(Integer)
    cpuData = db.Column(Integer)
    ramData = db.Column(Integer)

    # initialization of one raw in the database
    def __init__(self, containerName, realtime, cpuData, ramData):
        self.containerName = containerName
        self.realtime = realtime
        self.cpuData = cpuData
        self.ramData = ramData

    #def __repr__(self):
     #   return '<Request %r>' % (self.result)

#database class for the creation of a pseudo-DHCP mecanism
class Iport2(db.Model):
    # table name & components (creation)
    __tablename__ = 'portip2'
    id = db.Column(Integer, primary_key=True)
    ipaddress = db.Column(String(120))
    containerName = db.Column(String(120))
    port = db.Column(Integer)
    bool = db.Column(Integer)

    # initialization of one raw in the database
    def __init__(self, ipaddress, containerName, port, bool):
        self.ipaddress = ipaddress
        self.containerName = containerName
        self.port = port
        self.bool = bool







#function used to store Request information in the database
def store(id , results):
    process  = Mirai4.query.get(id)
    process.result = results
    db.session.commit()
    db.session.flush()




#functions used to store ip address & destroy them after finishing working with
def store_ip(id, bool, containerName):
    print ("test1")
    process = Iport2.query.get(id)
    print ("test2")
    process.bool = bool
    process.containerName = containerName
    db.session.commit()
    db.session.flush()

def destroy_ip(id, bool):
    print ("test1")
    process = Iport2.query.get(id)
    print ("test2")
    process.bool = bool
    process.containerName = "None"
    db.session.commit()
    db.session.flush()





#function to ensure the parallel processing
def ctrl(containerName):

    #do a global search in the data base by container name in order to ensure non-confusion & parallel processing
    found = Mirai4.query.filter_by(containerName=containerName).first()
    if found !=  None:

        print(found)
        return False
    return  True

#call a /index path and execute which is inside
@app.route('/index')
def index():

    # get a unique token
    token= uuid4()
    db.create_all()
    p = Mirai4.query.all()

    ################deleting monitoring part to always preserve the DB fresh###############
    m = Miraimonitor.query.all()
    for mm in m:
        db.session.delete(mm)
        db.session.commit()
    port = 0

    ################deleting ip address to renew the scenario of test###############
    n = Iport2.query.all()
    for nn in n:
        if (nn.bool == 1):
            destroy_ip(nn.id, 0)
    n = Iport2.query.all()
    ################showing the free IP address range###############
    for nn in n:
        print(nn.ipaddress)
        print(nn.port)
        print(nn.bool)
        print("##########")


    return render_template("index.html", token = token)

#call a /demo path and execute the home page
@app.route('/demo')
def demo():
    # get a unique token
    token= uuid4()
    db.create_all()
    p = Mirai4.query.all()


    port = 0

    ################deleting ip address to renew the scenario of test###############
    n = Iport2.query.all()
    for nn in n:
        if (nn.bool == 1):
            destroy_ip(nn.id, 0)

    return render_template("demo.html", token = token)

#to give back a response to the long polling
@app.route('/api/result',  methods=['GET','POST'])
def getResult():
    ################monitoring part ###############
    ramlimit = 1
    cpulimit = 2
    liste = monitor.containerList()
    for i in range(0, int(len(liste))):
        liveram = monitor.getLiveMem(liste[i])
        livecpu = monitor.getLiveCpu(liste[i])
        x = Miraimonitor(str(liste[i]), int(time.time()), int(livecpu), int(liveram))
        db.session.add(x)
        db.session.commit()
        #a request to get the last status from the DB for each container
        obj = Miraimonitor.query.filter(Miraimonitor.containerName==liste[i]).order_by(Miraimonitor.realtime.desc()).first()

        if (obj.ramData > ramlimit or obj.cpuData > cpulimit):
            print("migrate")
            #to activate the monitoring part we should call /api/migrate from here



    # an answer for the long-polling with the use of a code process to coordinate with the backend library
    p = Mirai4.query.all()
    print("############################")
    result = {}
    for pp in p:
        if pp.result != "None":

            # Json response to the front end after creation
            if pp.code == "001":
                info = pp.containerName
                resultDB = pp.result
                sendtoken = pp.token
                db.session.delete(pp)
                db.session.commit()
                data = {
                    'action': 'create',
                    'containerName': str(info),
                    'rsdb' : str(resultDB),
                    'token' : str(sendtoken)
                }
                js = json.dumps(data)
                resp = jsonify(data)
                resp.status_code = 200


                return resp
            # Json response to the front end after delete
            elif pp.code == '002':
                info = pp.containerName
                resultDB = pp.result
                sendtoken = pp.token

                db.session.delete(pp)
                db.session.commit()
                data = {
                    'action': 'delete',
                    'containerName': str(info),
                    'rsdb': str(resultDB),
                    'token': str(sendtoken)

                }
                resp = jsonify(data)
                resp.status_code = 200
                return resp
            # Json response to the front end after starting
            elif pp.code == '003':
                info = pp.containerName
                resultDB = pp.result
                sendtoken = pp.token

                db.session.delete(pp)
                db.session.commit()
                data = {
                    'action': 'start',
                    'containerName': str(info),
                    'rsdb': str(resultDB),
                    'token': str(sendtoken)

                }
                resp = jsonify(data)
                resp.status_code = 200
                return resp
            # Json response to the front end after stopping
            elif pp.code == '004':
                info = pp.containerName
                resultDB = pp.result
                sendtoken = pp.token

                db.session.delete(pp)
                db.session.commit()
                data = {
                    'action': 'stop',
                    'containerName': str(info),
                    'rsdb': str(resultDB),
                    'token': str(sendtoken)

                }
                resp = jsonify(data)
                resp.status_code = 200
                return resp
            # Json response to the front end after clonning
            elif pp.code == '005':
                info = pp.containerName
                resultDB = pp.result
                info2 = pp.newcontainerName
                sendtoken = pp.token

                db.session.delete(pp)
                db.session.commit()
                data = {
                    'action': 'clone',
                    'containerName': str(info),
                    'newcontainerName': str(info2),
                    'rsdb': str(resultDB),
                    'token': str(sendtoken)

                }
                resp = jsonify(data)
                resp.status_code = 200
                return resp
            # Json response to the front end after migration
            elif pp.code == '006':
                info = pp.containerName
                resultDB = pp.result
                sendtoken = pp.token

                db.session.delete(pp)
                db.session.commit()
                data = {
                    'action': 'migrate',
                    'containerName': str(info),
                    'rsdb': str(resultDB),
                    'token': str(sendtoken)

                }
                resp = jsonify(data)
                resp.status_code = 200
                return resp
            # Json response to the front end after getting information
            elif pp.code == '007':
                info = pp.containerName
                info2 = pp.result
                sendtoken = pp.token

                db.session.delete(pp)
                db.session.commit()
                temp = str(info2).split('#')
                if (str(info2) != "2"):
                    if (temp[2] == "RUNNING"):
                        data = {
                            'action': 'getinfo',
                            'containerName': str(info),
                            'token' : str(sendtoken),
                            'rsdb': temp[0],
                            'State': temp[2],
                            'PID': temp[3],
                            'IP': temp[4],
                            'CPU': temp[5],
                            'BlkIO': temp[6],
                            'Memory': temp[7],
                            'Link': temp[8],
                            'TXbytes': temp[9],
                            'RXbytes':temp[10]
                        }


                    else:
                        data = {
                            'action': 'getinfo',
                            'containerName': str(info),
                            'token' : str(sendtoken),
                            'rsdb': temp[0],
                            'State': temp[2]
                        }
                    resp = jsonify(data)
                    resp.status_code = 200
                    return resp
                else:
                    data = {
                        'action': 'getinfo',
                        'containerName': str(info),
                        'token': str(sendtoken),
                        'rsdb': str(info2),

                    }
                    resp = jsonify(data)
                    resp.status_code = 200
                    return resp


            else:
                print("wrong code please check the manual")
    return jsonify("nothing")


# communicating with the back-end and create the SDN-container
@app.route('/api/create', methods=['GET'])
def create():
    resp =""
    if request.is_xhr:
        containername = dict(request.args)['containername'][0]
        cpu = dict(request.args)['cpu'][0]
        ram = dict(request.args)['ram'][0]
        token1 =  dict(request.args)['token'][0]

        if (checking.nbrc(containername) == False):

            if ctrl(containername) ==  False:
                resp = jsonify("Error")
                print("Found it")
            else:
                print(Mirai4.query.all())
                x = Mirai4(str(containername), "001", "None", "None", str(token1))
                print(str(x.id))
                print(str(x.token))
                db.session.add(x)
                db.session.commit()

                t.producer1('001#' + str(x.id) + '#' + containername + '#' + cpu + '#' + ram, t.q1)
                t.consumer1(t.q1)

            print("after updating the request")
            print(Mirai4.query.all())
            m=Mirai4.query.all()
            for mm in m:
                print(mm.containerName)


            resp = jsonify(containername)
        else:
            print ("container already exist")
            x = Mirai4(str(containername), "001", "None", str(6), str(token))
            db.session.add(x)
            db.session.commit()

            print (str(x.id))
            print (x.result)

            store(x.id, str(2))
            resp = jsonify("Error")

    resp.status_code = 200
    return resp



# communicating with the back-end and delete the SDN-container
@app.route('/api/delete',  methods=['GET'])
def delete():
    resp =""

    if request.is_xhr:
        containername = dict(request.args)['containername'][0]
        token1 =  dict(request.args)['token'][0]

        if (checking.nbrc(containername) == True):
            if ctrl(containername) == False:
                resp = jsonify("Error")
                print("Found it")
            else:
                print(Mirai4.query.all())
                x = Mirai4(str(containername), "002", "None", "None", str(token1))
                print(str(x.id))
                db.session.add(x)
                db.session.commit()
                t.producer1('002#'+str(x.id)+'#' + containername, t.q1)
                t.consumer1(t.q1)
            resp = jsonify(containername)
        else:
            print ("container doesn't exist")
            x = Mirai4(str(containername), "002", "None", "None", str(token1))
            db.session.add(x)
            db.session.commit()

            print (str(x.id))
            print (x.result)

            store(x.id, str(2))
            resp = jsonify("Error")


    resp.status_code = 200
    return resp


# communicating with the back-end and start the container
@app.route('/api/start',  methods=['GET'])
def start():
    resp =""

    if request.is_xhr:
        containername = dict(request.args)['containername'][0]
        token1 =  dict(request.args)['token'][0]


        if (checking.nbrc(containername) == True):

            if ctrl(containername) == False:
                resp = jsonify("Error")
                print("Found it")
            else:
                x = Mirai4(str(containername), "003", "None", "None", str(token1))
                print(str(x.id))
                db.session.add(x)
                db.session.commit()
                print(Mirai4.query.all())
                t.producer1('003#'+str(x.id)+'#' + containername, t.q1)
                t.consumer1(t.q1)
            resp = jsonify(containername)
        else:
            print ("container doesn't exist")
            x = Mirai4(str(containername), "003", "None", "None", str(token1))
            db.session.add(x)
            db.session.commit()

            print (str(x.id))
            print (x.result)

            store(x.id, str(2))
            resp = jsonify("Error")


    resp.status_code = 200
    return resp



# communicating with the back-end and stop the container
@app.route('/api/stop',  methods=['GET'])
def stop():
    resp =""

    if request.is_xhr:
        containername = dict(request.args)['containername'][0]
        token1 =  dict(request.args)['token'][0]



        if (checking.nbrc(containername) == True):

            if ctrl(containername) == False:
                resp = jsonify("Error")
                print("Found it")
            else:
                x = Mirai4(str(containername), "004", "None", "None", str(token1))
                print(str(x.id))
                db.session.add(x)
                db.session.commit()
                print(Mirai4.query.all())
                t.producer1('004#'+str(x.id)+'#' + containername, t.q1)
                t.consumer1(t.q1)

            resp = jsonify(containername)
        else:
            print ("container doesn't exist")
            x = Mirai4(str(containername), "004", "None", "None", str(token1))
            db.session.add(x)
            db.session.commit()

            print (str(x.id))
            print (x.result)

            store(x.id, str(2))
            resp = jsonify("Error")

    resp.status_code = 200
    return resp



# communicating with the back-end and clone the container
@app.route('/api/clone',  methods=['GET'])
def clone():
    resp =""

    if request.is_xhr:
        containername = dict(request.args)['containername'][0]
        newcontainername = dict(request.args)['newcontainername'][0]
        token1 =  dict(request.args)['token'][0]


        if (checking.nbrc(containername) == True):

            if ctrl(containername) == False:
                resp = jsonify("Error")
                print("Found it")
            else:
                x = Mirai4(str(containername), "005", "None", str(newcontainername), str(token1))
                print(str(x.id))
                db.session.add(x)
                db.session.commit()
                print(Mirai4.query.all())
                y = Mirai4(str(newcontainername), "005", "None")
                print(str(y.id))
                db.session.add(y)
                db.session.commit()
                print(Mirai4.query.all())
                t.producer1('005#'+str(x.id)+'#' + containername + '#' + str(y.id) +'#'+ newcontainername, t.q1)
                t.consumer1(t.q1)

            resp = jsonify(containername)
        else:
            x = Mirai4(str(containername), "005", "None", str(newcontainername), str(token1))
            print(str(x.id))
            db.session.add(x)
            db.session.commit()
            print (str(x.id))
            print (x.result)

            store(x.id, str(2))
            resp = jsonify("Error")



    resp.status_code = 200
    return resp



#communicating with the back-end and migrate the container
@app.route('/api/migrate',  methods=['GET'])
def migrate():
    resp =""

    if request.is_xhr:
        containername = dict(request.args)['containername'][0]
        destIP = dict(request.args)['destIP'][0]
        numIntera = dict(request.args)['numIntera'][0]
        token1 =  dict(request.args)['token'][0]



        if (checking.nbrc(containername) == True):
            if (checking.remoteMigrationCheck(containername, destIP) == False):
                if (truechecking.callman(containername, destIP)== True):
                    if ctrl(str(containername)) == False:
                        resp = jsonify("Error")

                        print("Found it")
                    else:
                        x = Mirai4(str(containername), "006", "None", "None", str(token1))
                        print(str(x.id))
                        db.session.add(x)
                        db.session.commit()
                        print(Mirai4.query.all())
                        t.producer1('006#'+str(x.id)+'#' + containername + '#' + destIP + '#' + numIntera, t.q1)
                        t.consumer1(t.q1)

                    resp = jsonify(containername)
                else:
                    print ("not enough resorcess")
                    x = Mirai4(str(containername), "006", "None", "None", str(token1))
                    db.session.add(x)
                    db.session.commit()

                    print (str(x.id))
                    print (x.result)

                    store(x.id, str(8))
                    resp = jsonify("Error")

            else:
                print ("container has the same name in the remote host")
                x = Mirai4(str(containername), "006", "None", "None", str(token1))
                db.session.add(x)
                db.session.commit()

                print (str(x.id))
                print (x.result)

                store(x.id, str(10))
                resp = jsonify("Error")



        else:
            print ("container doesn't exist")
            x = Mirai4(str(containername), "006", "None", "None", str(token1))
            db.session.add(x)
            db.session.commit()

            print (str(x.id))
            print (x.result)

            store(x.id, str(2))
            resp = jsonify("Error")



    resp.status_code = 200
    return resp



#communicating with the back-end and get the info of the container
@app.route('/api/infos',  methods=['GET'])
def getInfo():
    resp =""

    if request.is_xhr:
        containername = dict(request.args)['containername'][0]
        token1 =  dict(request.args)['token'][0]



        if(checking.nbrc(containername) == True):
            if ctrl(containername) == False:
                resp = jsonify("Error")
                print("Found it")
            else:
                x = Mirai4(str(containername), "007", "None", "None", str(token1))
                print(str(x.id))
                db.session.add(x)
                db.session.commit()
                print(Mirai4.query.all())
                t.producer1('007#'+str(x.id)+'#' + containername, t.q1)
                t.consumer1(t.q1)

                resp = jsonify(containername)
        else:
            print ("container doesn't exist")
            x = Mirai4(str(containername), "007", "None", "None", str(token1))
            db.session.add(x)
            db.session.commit()

            print (str(x.id))
            print (x.result)

            store(x.id, str(2))
            resp = jsonify("Error")


    resp.status_code = 200
    return resp
