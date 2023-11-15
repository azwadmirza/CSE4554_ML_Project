    def write_smooth_raster_output(self,
                                   out_profile: dict,
                                   scores_path: str,
                                   hits_path: str,
                                   labels: SemanticSegmentationLabels,
                                   chip_sz: Optional[int] = None) -> None:
        dtype = np.uint8 if self.smooth_as_uint8 else np.float32

        out_profile.update({
            'count': labels.num_classes,
            'dtype': dtype,
        })
        if chip_sz is None:
            windows = [self.extent]
        else:
            windows = labels.get_windows(chip_sz=chip_sz)

        log.info('Writing smooth labels to disk.')
        with rio.open(scores_path, 'w', **out_profile) as dataset:
            with click.progressbar(windows) as bar:
                for window in bar:
                    window, _ = self._clip_to_extent(self.extent, window)
                    score_arr = labels.get_score_arr(window)
                    if self.smooth_as_uint8:
                        score_arr = self._scores_to_uint8(score_arr)
                    self._write_array(dataset, window, score_arr)
        # save pixel hits too
        np.save(hits_path, labels.pixel_hits)