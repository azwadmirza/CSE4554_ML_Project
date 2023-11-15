    def __init__(self, wallet_address):
        """
        :param wallet_address: String representation of a wallet address
        :type wallet_address: str
        :raises ValueError: Thrown when one of the arguments are invalid
        """
        super(WalletAddress, self).__init__()

        if not isinstance(wallet_address, str):
            raise ValueError("Wallet address must be a string")

        self._wallet_address = wallet_address