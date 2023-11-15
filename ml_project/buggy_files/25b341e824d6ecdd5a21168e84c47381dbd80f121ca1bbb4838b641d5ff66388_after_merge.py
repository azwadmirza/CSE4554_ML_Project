    def __init__(self, source_geo_def, target_geo_def):
        """Initialize bucket resampler."""
        super(BucketResamplerBase, self).__init__(source_geo_def, target_geo_def)
        self.resampler = None