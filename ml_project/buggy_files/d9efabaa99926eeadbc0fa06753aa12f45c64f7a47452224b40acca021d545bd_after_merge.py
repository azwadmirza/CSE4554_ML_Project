    def __init__(self, hs: "HomeServer"):
        super().__init__(hs)
        self.hs = hs
        self.auth = hs.get_auth()
        self.admin_handler = hs.get_admin_handler()
        self.state_handler = hs.get_state_handler()