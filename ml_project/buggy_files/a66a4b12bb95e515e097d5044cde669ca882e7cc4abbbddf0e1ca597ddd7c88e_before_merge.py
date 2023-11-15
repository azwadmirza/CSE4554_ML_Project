        def marginal(self, function_dist, *params, **kwargs):
            name_prefix = kwargs.get("name_prefix", "")
            num_samples = settings.num_likelihood_samples.value()
            with pyro.plate(name_prefix + ".num_particles_vectorized", num_samples, dim=(-self.max_plate_nesting - 1)):
                function_samples_shape = torch.Size(
                    [num_samples] + [1] * (self.max_plate_nesting - len(function_dist.batch_shape) - 1)
                )
                function_samples = function_dist(function_samples_shape)
                if self.training:
                    return self(function_samples, *params, **kwargs)
                else:
                    guide_trace = pyro.poutine.trace(self.guide).get_trace(*params, **kwargs)
                    marginal_fn = functools.partial(self.__call__, function_samples)
                    return pyro.poutine.replay(marginal_fn, trace=guide_trace)(*params, **kwargs)