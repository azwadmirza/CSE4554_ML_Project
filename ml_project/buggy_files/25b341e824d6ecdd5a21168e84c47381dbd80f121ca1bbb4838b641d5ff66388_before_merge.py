    def __init__(self, source_geo_def, target_geo_def):
        super(BucketResamplerBase, self).__init__(source_geo_def, target_geo_def)
        self.resampler = None