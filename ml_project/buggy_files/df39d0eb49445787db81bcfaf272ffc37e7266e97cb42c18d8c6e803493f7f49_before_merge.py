    def write_smooth_raster_output(self,
                                   out_smooth_profile: dict,
                                   scores_path: str,
                                   hits_path: str,
                                   labels: SemanticSegmentationLabels,
                                   chip_sz: Optional[int] = None) -> None:
        dtype = np.uint8 if self.smooth_as_uint8 else np.float32

        out_smooth_profile.update({
            'count': labels.num_classes,
            'dtype': dtype,
        })
        if chip_sz is None:
            windows = [self.extent]
        else:
            windows = labels.get_windows(chip_sz=chip_sz)

        log.info('Writing smooth labels to disk.')
        with rio.open(scores_path, 'w', **out_smooth_profile) as dataset:
            with click.progressbar(windows) as bar:
                for window in bar:
                    window = window.intersection(self.extent)
                    score_arr = labels.get_score_arr(window)
                    if self.smooth_as_uint8:
                        score_arr *= 255
                        score_arr = np.around(score_arr, out=score_arr)
                        score_arr = score_arr.astype(dtype)
                    window = window.rasterio_format()
                    for i, class_scores in enumerate(score_arr, start=1):
                        dataset.write_band(i, class_scores, window=window)
        # save pixel hits too
        np.save(hits_path, labels.pixel_hits)