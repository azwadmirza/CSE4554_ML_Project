    def __init__(self, slug=None, id=None):

        self.id = 0
        self.name = "Blank"
        self.description = "None"
        self.effect = []
        self.type = None
        self.power = 0
        self.sprite = ""                    # The path to the sprite to load.
        self.surface = None                 # The pygame.Surface object of the item.
        self.surface_size_original = (0, 0)  # The original size of the image before scaling.

        # If a slug of the item was provided, autoload it from the item database.
        if slug or id:
            self.load(slug, id)