    def __init__(self, hs: "HomeServer"):
        super().__init__(hs)
        self.hs = hs
        self.auth = hs.get_auth()
        self.store = hs.get_datastore()