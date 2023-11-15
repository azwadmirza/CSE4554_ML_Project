    def load_token_balance(self):
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("trustchain/statistics", self.received_trustchain_statistics,
                                         capture_errors=False)