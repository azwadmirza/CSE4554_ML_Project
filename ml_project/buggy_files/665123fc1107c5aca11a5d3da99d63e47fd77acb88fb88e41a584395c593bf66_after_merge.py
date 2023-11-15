    def to_pack_list(self):
        data = super(BalanceResponsePayload, self).to_pack_list()
        data.insert(0, ('I', self.circuit_id))
        return data