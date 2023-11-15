    def __init__(self, value):
        self.value = value
        super(Omitted, self).__init__("omitted(default=%r)" % (value,))