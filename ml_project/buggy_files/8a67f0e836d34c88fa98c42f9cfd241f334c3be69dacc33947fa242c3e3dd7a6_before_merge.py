    def save(self, labels):
        """Save.

        Args:
            labels - (SemanticSegmentationLabels) labels to be saved
        """
        local_path = get_local_path(self.uri, self.tmp_dir)
        make_dir(local_path, use_dirname=True)

        # TODO: this only works if crs_transformer is RasterioCRSTransformer.
        # Need more general way of computing transform for the more general case.
        transform = self.crs_transformer.transform
        crs = self.crs_transformer.get_image_crs()

        band_count = 1
        dtype = np.uint8
        if self.class_trans:
            band_count = 3

        if self.vector_output:
            # We need to store the whole output mask to run feature extraction.
            # If the raster is large, this will result in running out of memory, so
            # more work will be needed to get this to work in a scalable way. But this
            # is complicated because of the need to merge features that are split
            # across windows.
            mask = np.zeros(
                (self.extent.ymax, self.extent.xmax), dtype=np.uint8)
        else:
            mask = None

        # https://github.com/mapbox/rasterio/blob/master/docs/quickstart.rst
        # https://rasterio.readthedocs.io/en/latest/topics/windowed-rw.html
        with rasterio.open(
                local_path,
                'w',
                driver='GTiff',
                height=self.extent.ymax,
                width=self.extent.xmax,
                count=band_count,
                dtype=dtype,
                transform=transform,
                crs=crs) as dataset:
            for window in labels.get_windows():
                class_labels = labels.get_label_arr(
                    window, clip_extent=self.extent)
                clipped_window = ((window.ymin,
                                   window.ymin + class_labels.shape[0]),
                                  (window.xmin,
                                   window.xmin + class_labels.shape[1]))
                if mask is not None:
                    mask[clipped_window[0][0]:clipped_window[0][1],
                         clipped_window[1][0]:clipped_window[1][
                             1]] = class_labels
                if self.class_trans:
                    rgb_labels = self.class_trans.class_to_rgb(class_labels)
                    for chan in range(3):
                        dataset.write_band(
                            chan + 1,
                            rgb_labels[:, :, chan],
                            window=clipped_window)
                else:
                    img = class_labels.astype(dtype)
                    dataset.write_band(1, img, window=clipped_window)

        upload_or_copy(local_path, self.uri)

        if self.vector_output:
            import mask_to_polygons.vectorification as vectorification
            import mask_to_polygons.processing.denoise as denoise

            for vo in self.vector_output:
                denoise_radius = vo['denoise']
                uri = vo['uri']
                mode = vo['mode']
                class_id = vo['class_id']
                class_mask = np.array(mask == class_id, dtype=np.uint8)
                local_geojson_path = get_local_path(uri, self.tmp_dir)

                def transform(x, y):
                    return self.crs_transformer.pixel_to_map((x, y))

                if denoise_radius > 0:
                    class_mask = denoise.denoise(class_mask, denoise_radius)

                if uri and mode == 'buildings':
                    options = vo['building_options']
                    geojson = vectorification.geojson_from_mask(
                        mask=class_mask,
                        transform=transform,
                        mode=mode,
                        min_aspect_ratio=options['min_aspect_ratio'],
                        min_area=options['min_area'],
                        width_factor=options['element_width_factor'],
                        thickness=options['element_thickness'])
                elif uri and mode == 'polygons':
                    geojson = vectorification.geojson_from_mask(
                        mask=class_mask, transform=transform, mode=mode)

                if local_geojson_path:
                    with open(local_geojson_path, 'w') as file_out:
                        file_out.write(geojson)
                        upload_or_copy(local_geojson_path, uri)