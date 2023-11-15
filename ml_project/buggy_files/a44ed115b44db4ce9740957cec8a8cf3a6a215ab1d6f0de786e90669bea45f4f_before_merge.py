    def write_discrete_raster_output(
            self, out_smooth_profile: dict, path: str,
            labels: SemanticSegmentationLabels) -> None:

        num_bands = 1 if self.class_transformer is None else 3
        out_smooth_profile.update({'count': num_bands, 'dtype': np.uint8})

        windows = labels.get_windows()

        log.info('Writing labels to disk.')
        with rio.open(path, 'w', **out_smooth_profile) as dataset:
            with click.progressbar(windows) as bar:
                for window in bar:
                    window = window.intersection(self.extent)
                    label_arr = labels.get_label_arr(window)
                    window = window.rasterio_format()
                    if self.class_transformer is None:
                        dataset.write_band(1, label_arr, window=window)
                    else:
                        rgb_labels = self.class_transformer.class_to_rgb(
                            label_arr)
                        rgb_labels = rgb_labels.transpose(2, 0, 1)
                        for i, band in enumerate(rgb_labels, start=1):
                            dataset.write_band(i, band, window=window)