    def __init__(self, name=None, id=None):
        self.name = "Pound"
        self.tech_id = 0
        self.category = "attack"
        self.type1 = "Normal"
        self.type2 = None
        self._combat_counter = 0     # number of turns that this technique has been active
        self.power = 1
        self.effect = []

        # If a name of the technique was provided, autoload it.
        if name or id:
            self.load(name, id)