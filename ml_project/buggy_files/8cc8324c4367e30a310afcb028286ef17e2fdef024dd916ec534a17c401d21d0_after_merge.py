    def stopServer(self):
        # ToDo: Somehow caused by circular import under python3 refactor
        if sys.version_info > (3, 0):
            if not self.wsgiserver:
                if gevent_present:
                    self.wsgiserver = web.py3_gevent_link
                else:
                    self.wsgiserver = IOLoop.instance()
        if self.wsgiserver:
            if gevent_present:
                self.wsgiserver.close()
            else:
                self.wsgiserver.add_callback(self.wsgiserver.stop)