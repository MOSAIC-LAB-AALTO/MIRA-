


#This is the acknowledgement callback that confirm that create container request was received by the client
def createAck(containerName):
   print(" Container creation using webSocket, containerNAme"+str(containerName))

def migrateAck(containerName):
   print(" container migration using webSocket, containerName"+str(containerName))
