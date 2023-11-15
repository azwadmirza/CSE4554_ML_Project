    def _delete_cookie(self):
        self.request['set_cookie'] = True
        self.cookie[self.key] = self.id
        if self._domain:
            self.cookie[self.key]['domain'] = self._domain
        if self.secure:
            self.cookie[self.key]['secure'] = True
        self.cookie[self.key]['path'] = '/'
        expires = datetime.today().replace(year=2003)
        self.cookie[self.key]['expires'] = \
            expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT" )
        self.request['cookie_out'] = self.cookie[self.key].output(header='')
        self.request['set_cookie'] = True