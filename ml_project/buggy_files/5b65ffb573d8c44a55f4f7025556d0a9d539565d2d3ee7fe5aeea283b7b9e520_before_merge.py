    def check_consistent_shape(self) -> None:
        shapes_dict = {}
        iterable = self.get_images_dict(intensity_only=False).items()
        for image_name, image in iterable:
            shapes_dict[image_name] = image.shape
        num_unique_shapes = len(set(shapes_dict.values()))
        if num_unique_shapes > 1:
            message = (
                'Images in subject have inconsistent shapes:'
                f'\n{pprint.pformat(shapes_dict)}'
            )
            raise ValueError(message)