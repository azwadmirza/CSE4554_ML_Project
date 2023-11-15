    def build(self, class_config, crs_transformer, extent, tmp_dir):
        return SemanticSegmentationLabelStore(
            self.uri,
            extent,
            crs_transformer,
            tmp_dir,
            vector_output=self.vector_output,
            class_config=class_config if self.rgb else None)