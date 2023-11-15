    def save(self, labels):
        """Save.

        Args:
            labels - (SemanticSegmentationLabels) labels to be saved
        """
        local_path = get_local_path(self.uri, self.tmp_dir)
        make_dir(local_path, use_dirname=True)

        transform = self.crs_transformer.get_affine_transform()
        crs = self.crs_transformer.get_image_crs()

        band_count = 1
        dtype = np.uint8
        if self.class_trans:
            band_count = 3

        mask = (np.zeros((self.extent.ymax, self.extent.xmax), dtype=np.uint8)
                if self.vector_output else None)

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
                label_arr = labels.get_label_arr(window)
                window = window.intersection(self.extent)
                label_arr = label_arr[0:window.get_height(), 0:
                                      window.get_width()]

                if mask is not None:
                    mask[window.ymin:window.ymax, window.xmin:
                         window.xmax] = label_arr

                window = window.rasterio_format()
                if self.class_trans:
                    rgb_labels = self.class_trans.class_to_rgb(label_arr)
                    for chan in range(3):
                        dataset.write_band(
                            chan + 1, rgb_labels[:, :, chan], window=window)
                else:
                    img = label_arr.astype(dtype)
                    dataset.write_band(1, img, window=window)

        upload_or_copy(local_path, self.uri)

        if self.vector_output:
            import mask_to_polygons.vectorification as vectorification
            import mask_to_polygons.processing.denoise as denoise

            for vo in self.vector_output:
                denoise_radius = vo.denoise
                uri = vo.uri
                mode = vo.get_mode()
                class_id = vo.class_id
                class_mask = np.array(mask == class_id, dtype=np.uint8)

                def transform(x, y):
                    return self.crs_transformer.pixel_to_map((x, y))

                if denoise_radius > 0:
                    class_mask = denoise.denoise(class_mask, denoise_radius)

                if uri and mode == 'buildings':
                    geojson = vectorification.geojson_from_mask(
                        mask=class_mask,
                        transform=transform,
                        mode=mode,
                        min_aspect_ratio=vo.min_aspect_ratio,
                        min_area=vo.min_area,
                        width_factor=vo.element_width_factor,
                        thickness=vo.element_thickness)
                elif uri and mode == 'polygons':
                    geojson = vectorification.geojson_from_mask(
                        mask=class_mask, transform=transform, mode=mode)
                str_to_file(geojson, uri)