    def loss_and_grads(self, model, guide, *args, **kwargs):
        """
        :returns: returns an estimate of the ELBO
        :rtype: float

        Computes the ELBO as well as the surrogate ELBO that is used to form the gradient estimator.
        Performs backward on the latter. Num_particle many samples are used to form the estimators.
        """
        elbo = 0.0
        # grab a trace from the generator
        for weight, model_trace, guide_trace, log_r in self._get_traces(model, guide, *args, **kwargs):
            elbo_particle = weight * 0
            surrogate_elbo_particle = weight * 0
            # compute elbo and surrogate elbo
            if (self.enum_discrete and isinstance(weight, Variable) and weight.size(0) > 1):
                log_pdf = "batch_log_pdf"
            else:
                log_pdf = "log_pdf"
            for name, model_site in model_trace.nodes.items():
                if model_site["type"] == "sample":
                    if model_site["is_observed"]:
                        elbo_particle += model_site[log_pdf]
                        surrogate_elbo_particle += model_site[log_pdf]
                    else:
                        guide_site = guide_trace.nodes[name]
                        lp_lq = model_site[log_pdf] - guide_site[log_pdf]
                        elbo_particle += lp_lq
                        if guide_site["fn"].reparameterized:
                            surrogate_elbo_particle += lp_lq
                        else:
                            # XXX should the user be able to control inclusion of the -logq term below?
                            guide_log_pdf = guide_site[log_pdf] / guide_site["scale"]  # not scaled by subsampling
                            surrogate_elbo_particle += model_site[log_pdf] + log_r.detach() * guide_log_pdf

            # drop terms of weight zero to avoid nans
            if isinstance(weight, numbers.Number):
                if weight == 0.0:
                    elbo_particle = torch_zeros_like(elbo_particle)
                    surrogate_elbo_particle = torch_zeros_like(surrogate_elbo_particle)
            else:
                weight_eq_zero = (weight == 0)
                elbo_particle[weight_eq_zero] = 0.0
                surrogate_elbo_particle[weight_eq_zero] = 0.0

            elbo += torch_data_sum(weight * elbo_particle)
            surrogate_elbo_particle = torch_sum(weight * surrogate_elbo_particle)

            # collect parameters to train from model and guide
            trainable_params = set(site["value"]
                                   for trace in (model_trace, guide_trace)
                                   for site in trace.nodes.values()
                                   if site["type"] == "param")

            if trainable_params:
                surrogate_loss_particle = -surrogate_elbo_particle
                torch_backward(surrogate_loss_particle)
                pyro.get_param_store().mark_params_active(trainable_params)

        loss = -elbo
        if np.isnan(loss):
            warnings.warn('Encountered NAN loss')
        return loss