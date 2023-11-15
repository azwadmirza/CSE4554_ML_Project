    def __init__(self, *args, **kwargs):
        """Create a new Dataset instance."""
        self._parent_encoding = kwargs.get('parent_encoding', default_encoding)
        if not args:
            self.tags = {}
        elif isinstance(args[0], Dataset):
            self.tags = args[0].tags
        else:
            self.tags = args[0]
        self.is_decompressed = False

        # the following read_XXX attributes are used internally to store
        # the properties of the dataset after read from a file

        # set depending on the endianess of the read dataset
        self.read_little_endian = None
        # set depending on the VR handling of the read dataset
        self.read_implicit_vr = None
        # set to the encoding the dataset had originally
        self.read_encoding = None

        self.is_little_endian = None
        self.is_implicit_VR = None