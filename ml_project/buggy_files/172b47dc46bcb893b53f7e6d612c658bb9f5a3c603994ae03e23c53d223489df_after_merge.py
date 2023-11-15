    def __init__(self, wallet_address):
        """
        :param wallet_address: String representation of a wallet address
        :type wallet_address: str or unicode
        :raises ValueError: Thrown when one of the arguments are invalid
        """
        super(WalletAddress, self).__init__()

        if not isinstance(wallet_address, string_types):
            raise ValueError("Wallet address must be a string, found %s instead" % type(wallet_address))

        self._wallet_address = wallet_address