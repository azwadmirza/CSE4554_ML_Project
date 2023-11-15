    def __create_bidder(self, registry, transacting: bool = False, hw_wallet: bool = False):
        client_password = None
        if transacting and not hw_wallet:
            client_password = get_client_password(checksum_address=self.bidder_address)
        bidder = Bidder(checksum_address=self.bidder_address, registry=registry, client_password=client_password)
        return bidder