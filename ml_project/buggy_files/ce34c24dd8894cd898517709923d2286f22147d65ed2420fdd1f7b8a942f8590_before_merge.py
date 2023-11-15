    def __init__(self, **kwd):
        Binary.__init__(self, **kwd)

        """The header file. Provides information about dimensions, identification, and processing history."""
        self.add_composite_file(
            'hdr',
            description='The Analyze75 header file.',
            is_binary=False)

        """The image file.  Image data, whose data type and ordering are described by the header file."""
        self.add_composite_file(
            'img',
            description='The Analyze75 image file.',
            is_binary=True)

        """The optional t2m file."""
        self.add_composite_file(
            't2m',
            description='The Analyze75 t2m file.',
            optional='True', is_binary=True)