import multiprocessing
import migrateLXC
import time
import NothBoundLayer


NOK = -1
OK = 1

# please change the address of your controller as you need
IPSDN = "192.168.122.208"

# class used in order to implement the parallel logic
class producer():


    def __init__(self):
        self.q1 = multiprocessing.Queue()



    def producer1(self, code, q):
        producer = multiprocessing.Process(target=self.northboundToQ1, args=(code,q))
        producer.start()
        producer.join()




    def consumer1(self, q):
        consumer = multiprocessing.Process(target=self.q1ToSouthbound, args=(q,))
        consumer.start()
        consumer.join()







    #function used to push in the queue from the web interface
    def northboundToQ1(self, code, q):
        print("i received " + str(code))
        q.put(code)


    #function used to pull from the queue, the library will pull from the queue and use this informations to do the Request asked from the web part
    def q1ToSouthbound(self, q):


        g=migrateLXC.api()
        while q.empty() is not False:
            print("waiting ... waiting ...")
        resultInfo = q.get()
        myInfo = resultInfo.split('#')
        code = myInfo[0]
        idDB = myInfo[1]
        containerName = myInfo[2]

        result = NOK
        result2 = NOK

        if code =='001':
            cpu = myInfo[3]
            ram = myInfo[4]
            result = g.createnginx(str(containerName), cpu, ram, IPSDN)
        elif code == '002':
            result = g.delete(containerName)
        elif code == '003':
            result = g.start(containerName)
        elif code == '004':
            result = g.stop(containerName)
        elif code == '005':
            idDB2 = myInfo[3]
            newContainerName = myInfo[4]
            result2 = g.clone(containerName,newContainerName)
            result = result2
            NothBoundLayer.store(idDB2, str(result2))
        elif code == '006':
            destIP = myInfo[3]
            numIntera = myInfo[4]
            result = g.migrate(str(containerName),destIP,numIntera, IPSDN)
        elif code == '007':
            result = g.detailedInfo(containerName)

        else:
            print("wrong code please check the manual")


        NothBoundLayer.store(idDB, str(result))


