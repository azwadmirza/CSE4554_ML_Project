    def __init__(self, feature):
        super().__init__(feature)

        self.height = 0
        self.width = 0
        self.num_channels = 0

        self.in_memory = True

        self.encoder = 'stacked_cnn'

        encoder_parameters = self.overwrite_defaults(feature)

        self.encoder_obj = self.get_image_encoder(encoder_parameters)