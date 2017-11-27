import globalCtrl



class mainclass():
    def __init__(self):
        self.x= globalCtrl.Ctrl()
    def callman(self, containerName, destIP):
        self.x.sourceChecking(containerName)
        return self.x.destinationChecking(containerName, destIP)
