    def __init__(self, network, wallet):
        self.wallet = wallet
        self.network = network
        self.blockchain = network.blockchain()
        # Keyed by tx hash.  Value is None if the merkle branch was
        # requested, and the merkle root once it has been verified
        self.merkle_roots = {}
        self.requested_chunks = {}