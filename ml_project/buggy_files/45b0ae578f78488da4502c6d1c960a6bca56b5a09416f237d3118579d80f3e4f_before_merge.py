    def rescale_parameters(
        self, parameters: torch.Tensor, target_scale: torch.Tensor, encoder: BaseEstimator
    ) -> torch.Tensor:
        assert encoder.transformation in ["logit"], "Beta distribution is only compatible with logit transformation"
        assert encoder.center, "Beta distribution requires normalizer to center data"

        scaled_mean = encoder(dict(prediction=parameters[..., 0], target_scale=target_scale))
        # need to first transform target scale standard deviation in logit space to real space
        # we assume a normal distribution in logit space (we used a logit transform and a standard scaler)
        # and know that the variance of the beta distribution is limited by `scaled_mean * (1 - scaled_mean)`
        mean_derivative = scaled_mean * (1 - scaled_mean)

        # we can approximate variance as
        # torch.pow(torch.tanh(target_scale[..., 1].unsqueeze(1) * torch.sqrt(mean_derivative)), 2) * mean_derivative
        # shape is (positive) parameter * mean_derivative / var
        shape_scaler = torch.pow(torch.tanh(target_scale[..., 1].unsqueeze(1) * torch.sqrt(mean_derivative)), 2)
        scaled_shape = F.softplus(parameters[..., 1]) / shape_scaler
        return torch.stack([scaled_mean, scaled_shape], dim=-1)