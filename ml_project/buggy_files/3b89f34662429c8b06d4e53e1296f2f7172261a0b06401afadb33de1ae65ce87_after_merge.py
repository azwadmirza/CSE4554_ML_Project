    def apply_transform(self, sample: Subject) -> dict:
        sample.check_consistent_spatial_shape()
        params = self.get_params(
            self.scales,
            self.degrees,
            self.translation,
            self.isotropic,
        )
        scaling_params, rotation_params, translation_params = params
        for image in self.get_images(sample):
            if image[TYPE] != INTENSITY:
                interpolation = Interpolation.NEAREST
            else:
                interpolation = self.interpolation

            if image.is_2d():
                scaling_params[0] = 1
                rotation_params[-2:] = 0

            if self.use_image_center:
                center = image.get_center(lps=True)
            else:
                center = None

            transformed_tensors = []
            for tensor in image[DATA]:
                transformed_tensor = self.apply_affine_transform(
                    tensor,
                    image[AFFINE],
                    scaling_params.tolist(),
                    rotation_params.tolist(),
                    translation_params.tolist(),
                    interpolation,
                    center_lps=center,
                )
                transformed_tensors.append(transformed_tensor)
            image[DATA] = torch.stack(transformed_tensors)
        random_parameters_dict = {
            'scaling': scaling_params,
            'rotation': rotation_params,
            'translation': translation_params,
        }
        sample.add_transform(self, random_parameters_dict)
        return sample