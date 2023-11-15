    def apply_transform(self, sample: Subject) -> dict:
        sample.check_consistent_spatial_shape()
        bspline_params = self.get_params(
            self.num_control_points,
            self.max_displacement,
            self.num_locked_borders,
        )
        for image in self.get_images(sample):
            if image[TYPE] != INTENSITY:
                interpolation = Interpolation.NEAREST
            else:
                interpolation = self.interpolation
            if image.is_2d():
                bspline_params[..., -3] = 0  # no displacement in LR axis
            image[DATA] = self.apply_bspline_transform(
                image[DATA],
                image[AFFINE],
                bspline_params,
                interpolation,
            )
        random_parameters_dict = {'coarse_grid': bspline_params}
        sample.add_transform(self, random_parameters_dict)
        return sample