    def __init__(self, hs: GenericWorkerServer):
        self.store = hs.get_datastore()
        self._is_mine_id = hs.is_mine_id
        self.federation_sender = hs.get_federation_sender()
        self._hs = hs

        # if the worker is restarted, we want to pick up where we left off in
        # the replication stream, so load the position from the database.
        #
        # XXX is this actually worthwhile? Whenever the master is restarted, we'll
        # drop some rows anyway (which is mostly fine because we're only dropping
        # typing and presence notifications). If the replication stream is
        # unreliable, why do we do all this hoop-jumping to store the position in the
        # database? See also https://github.com/matrix-org/synapse/issues/7535.
        #
        self.federation_position = self.store.federation_out_pos_startup

        self._fed_position_linearizer = Linearizer(name="_fed_position_linearizer")
        self._last_ack = self.federation_position