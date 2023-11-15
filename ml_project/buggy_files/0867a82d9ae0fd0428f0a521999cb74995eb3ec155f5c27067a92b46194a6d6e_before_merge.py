    def save(self, labels: SemanticSegmentationLabels) -> None:
        """Save labels to disk.

        More info on rasterio IO:
        - https://github.com/mapbox/rasterio/blob/master/docs/quickstart.rst
        - https://rasterio.readthedocs.io/en/latest/topics/windowed-rw.html

        Args:
            labels - (SemanticSegmentationLabels) labels to be saved
        """
        local_root = get_local_path(self.root_uri, self.tmp_dir)
        make_dir(local_root)

        out_smooth_profile = {
            'driver': 'GTiff',
            'height': self.extent.ymax,
            'width': self.extent.xmax,
            'transform': self.crs_transformer.get_affine_transform(),
            'crs': self.crs_transformer.get_image_crs(),
            'blockxsize': self.rasterio_block_size,
            'blockysize': self.rasterio_block_size
        }

        # if old scores exist, combine them with the new ones
        if self.score_raster_source:
            log.info('Old scores found. Merging with current scores.')
            old_labels = self.get_scores()
            labels += old_labels

        self.write_discrete_raster_output(
            out_smooth_profile, get_local_path(self.label_uri, self.tmp_dir),
            labels)

        if self.smooth_output:
            self.write_smooth_raster_output(
                out_smooth_profile,
                get_local_path(self.score_uri, self.tmp_dir),
                get_local_path(self.hits_uri, self.tmp_dir),
                labels,
                chip_sz=self.rasterio_block_size)

        if self.vector_outputs:
            self.write_vector_outputs(labels)

        sync_to_dir(local_root, self.root_uri)