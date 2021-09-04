class FileSerializer():
    def __init__(self,file):
        self.file = file
        data = file.readlines()
        for datum in data:
            field,value = datum.split('=') if type(datum)==str else datum.decode('utf8').split('=')
            self.__setattr__(field,value)

    def save(self):
        self.file.write()
        self.file.close()


