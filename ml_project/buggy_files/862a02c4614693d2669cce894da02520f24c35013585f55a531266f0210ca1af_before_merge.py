    def __init__(self, hs: "HomeServer"):
        self.hs = hs
        self.auth = hs.get_auth()
        self.room_member_handler = hs.get_room_member_handler()
        self.store = hs.get_datastore()