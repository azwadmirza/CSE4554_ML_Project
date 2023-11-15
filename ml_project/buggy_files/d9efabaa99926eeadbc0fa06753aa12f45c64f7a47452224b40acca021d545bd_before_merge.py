    def __init__(self, hs: "HomeServer"):
        self.hs = hs
        self.auth = hs.get_auth()
        self.room_member_handler = hs.get_room_member_handler()
        self.admin_handler = hs.get_admin_handler()
        self.state_handler = hs.get_state_handler()