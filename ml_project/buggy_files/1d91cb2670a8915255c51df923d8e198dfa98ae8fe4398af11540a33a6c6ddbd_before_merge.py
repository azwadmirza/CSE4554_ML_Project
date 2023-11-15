    def __init__(self, array):
        """ This adapter is usually called in Variable.__getitem__ with
        array=Variable._broadcast_indexes
        """
        self.array = array