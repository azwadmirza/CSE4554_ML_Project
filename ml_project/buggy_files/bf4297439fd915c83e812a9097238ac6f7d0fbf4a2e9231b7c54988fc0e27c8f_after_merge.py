    def __init__(self, hs: "HomeServer"):
        super().__init__(hs)
        self.hs = hs
        self.auth = hs.get_auth()
        self.event_creation_handler = hs.get_event_creation_handler()
        self.state_handler = hs.get_state_handler()
        self.is_mine_id = hs.is_mine_id