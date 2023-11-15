    def write_discrete_raster_output(
            self, out_profile: dict, path: str,
            labels: SemanticSegmentationLabels) -> None:

        num_bands = 1 if self.class_transformer is None else 3
        out_profile.update({'count': num_bands, 'dtype': np.uint8})

        windows = labels.get_windows()

        log.info('Writing labels to disk.')
        with rio.open(path, 'w', **out_profile) as dataset:
            with click.progressbar(windows) as bar:
                for window in bar:
                    label_arr = labels.get_label_arr(window)
                    window, label_arr = self._clip_to_extent(
                        self.extent, window, label_arr)
                    if self.class_transformer is not None:
                        label_arr = self.class_transformer.class_to_rgb(
                            label_arr)
                        label_arr = label_arr.transpose(2, 0, 1)
                    self._write_array(dataset, window, label_arr)