    def _get_sample_shape(sample: Subject) -> TypeTripletInt:
        """Return the shape of the first image in the sample."""
        sample.check_consistent_spatial_shape()
        for image_dict in sample.get_images(intensity_only=False):
            data = image_dict.spatial_shape  # remove channels dimension
            break
        return data