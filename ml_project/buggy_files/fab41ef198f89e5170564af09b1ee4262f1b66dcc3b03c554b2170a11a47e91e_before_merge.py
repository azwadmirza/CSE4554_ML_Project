    def _labels_to_full_label_arr(
            self, labels: SemanticSegmentationLabels) -> np.ndarray:
        """Get an array of labels covering the full extent."""
        try:
            label_arr = labels.get_label_arr(self.extent)
            return label_arr
        except KeyError:
            pass

        # construct the array from individual windows
        windows = labels.get_windows()

        # value for pixels not convered by any windows
        try:
            default_class_id = self.class_config.get_null_class_id()
        except ValueError:
            # Set it to a high value so that it doesn't match any class's id.
            # assumption: num_classes < 256
            default_class_id = 255

        label_arr = np.full(
            self.extent.size, fill_value=default_class_id, dtype=np.uint8)

        for w in windows:
            w = w.intersection(self.extent)
            ymin, xmin, ymax, xmax = w
            arr = labels.get_label_arr(w)
            label_arr[ymin:ymax, xmin:xmax] = arr
        return label_arr