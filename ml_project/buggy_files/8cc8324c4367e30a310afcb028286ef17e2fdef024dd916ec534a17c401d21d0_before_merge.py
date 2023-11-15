    def stopServer(self):
        if gevent_present:
            self.wsgiserver.close()
        else:
            self.wsgiserver.add_callback(self.wsgiserver.stop)