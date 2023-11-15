    def set_included_files(self, files):
        data_str = ''.join("selected_files[]=%s&" % ind for ind in files)[:-1]
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("downloads/%s" % self.current_download['infohash'], lambda _: None,
                                         method='PATCH', data=data_str)