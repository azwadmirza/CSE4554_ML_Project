    def __init__(self, slug=None, id=None):
        self.name = "Pound"
        self.tech_id = 0
        self.category = "attack"
        self.type1 = "Normal"
        self.type2 = None
        self._combat_counter = 0     # number of turns that this technique has been active
        self.power = 1
        self.effect = []

        # If a slug of the technique was provided, autoload it.
        if slug or id:
            self.load(slug, id)