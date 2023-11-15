    def set_included_files(self, files):
        data_str = ''.join(u"selected_files[]=%s&" % quote_plus(file) for file in files)[:-1].encode('utf-8')
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("downloads/%s" % self.current_download['infohash'], lambda _: None,
                                         method='PATCH', data=data_str)