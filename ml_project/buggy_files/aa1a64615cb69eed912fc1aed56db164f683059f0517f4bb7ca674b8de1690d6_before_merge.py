    def createActualFile(self, fileName, toOPML, toZip):
        if toZip:
            self.toString = True
            theActualFile = None
        else:
            try:
                # 2010/01/21: always write in binary mode.
                theActualFile = open(fileName, 'wb')
            except IOError:
                g.es(f"can not open {fileName}")
                g.es_exception()
                theActualFile = None
        return fileName, theActualFile