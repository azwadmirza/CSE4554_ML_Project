    def __init__(self, array):
        """ This adapter is created in Variable.__getitem__ in
        Variable._broadcast_indexes.
        """
        self.array = array