    def __init__(self, hs: GenericWorkerServer, replication_client):
        self.store = hs.get_datastore()
        self._is_mine_id = hs.is_mine_id
        self.federation_sender = hs.get_federation_sender()
        self.replication_client = replication_client

        self.federation_position = self.store.federation_out_pos_startup
        self._fed_position_linearizer = Linearizer(name="_fed_position_linearizer")

        self._last_ack = self.federation_position

        self._room_serials = {}
        self._room_typing = {}