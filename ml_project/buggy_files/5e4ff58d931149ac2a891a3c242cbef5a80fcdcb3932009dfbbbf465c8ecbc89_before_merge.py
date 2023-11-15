    def __init__(self, images=None, objects=None, masks=None, interpolation=None):
        """Initialize the artist with the images and objects"""
        super(CPImageArtist, self).__init__()
        self.__images = images or []
        self.__objects = objects or []
        self.__masks = masks or []
        self.__interpolation = interpolation
        self.filterrad = 4.0