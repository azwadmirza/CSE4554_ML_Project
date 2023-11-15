    def _compute_grid(self, inputs):
        n_data, n_dimensions = inputs.size(-2), inputs.size(-1)
        batch_shape = inputs.shape[:-2]

        inputs = inputs.reshape(-1, n_dimensions)
        interp_indices, interp_values = Interpolation().interpolate(self.grid, inputs)
        interp_indices = interp_indices.view(*batch_shape, n_data, -1)
        interp_values = interp_values.view(*batch_shape, n_data, -1)

        if (interp_indices.dim() - 2) != len(self._variational_distribution.batch_shape):
            batch_shape = _mul_broadcast_shape(interp_indices.shape[:-2], self._variational_distribution.batch_shape)
            interp_indices = interp_indices.expand(*batch_shape, *interp_indices.shape[-2:])
            interp_values = interp_values.expand(*batch_shape, *interp_values.shape[-2:])
        return interp_indices, interp_values