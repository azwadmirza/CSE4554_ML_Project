    def on_subscribe_button_click(self):
        if self.channel_info["state"] == "Personal" or self.channel_info["status"] == 1000:
            return
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("metadata/channels/%s/%i" %
                                         (self.channel_info[u'public_key'], self.channel_info[u'id']),
                                         lambda data: self.update_subscribe_button(remote_response=data),
                                         data={"subscribe": int(not self.channel_info["subscribed"])}, method='POST')