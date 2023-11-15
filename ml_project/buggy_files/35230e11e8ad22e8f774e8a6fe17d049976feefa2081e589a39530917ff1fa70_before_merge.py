    def step(self, x: Dict[str, torch.Tensor], y: torch.Tensor, batch_idx: int, label="train"):
        """
        Run for each train/val step.
        """
        # pack y sequence if different encoder lengths exist
        if (x["decoder_lengths"] < x["decoder_lengths"].max()).any():
            y = rnn.pack_padded_sequence(y, lengths=x["decoder_lengths"], batch_first=True, enforce_sorted=False)

        if label == "train" and len(self.hparams.monotone_constaints) > 0:
            # calculate gradient with respect to continous decoder features
            x["decoder_cont"].requires_grad_(True)
            assert not torch._C._get_cudnn_enabled(), (
                "To use monotone constraints, wrap model and training in context "
                "`torch.backends.cudnn.flags(enable=False)`"
            )
            out = self(x)
            out["prediction"] = self.transform_output(out)
            prediction = out["prediction"]

            gradient = torch.autograd.grad(
                outputs=prediction,
                inputs=x["decoder_cont"],
                grad_outputs=torch.ones_like(prediction),  # t
                create_graph=True,  # allows usage in graph
                allow_unused=True,
            )[0]

            # select relevant features
            indices = torch.tensor(
                [self.hparams.x_reals.index(name) for name in self.hparams.monotone_constaints.keys()]
            )
            monotonicity = torch.tensor(
                [val for val in self.hparams.monotone_constaints.values()], dtype=gradient.dtype, device=gradient.device
            )
            # add additionl loss if gradient points in wrong direction
            gradient = gradient[..., indices] * monotonicity[None, None]
            monotinicity_loss = gradient.clamp_max(0).mean()
            # multiply monotinicity loss by large number to ensure relevance and take to the power of 2
            # for smoothness of loss function
            monotinicity_loss = 10 * torch.pow(monotinicity_loss, 2)
            if isinstance(self.loss, MASE):
                loss = self.loss(
                    prediction, y, encoder_target=x["encoder_target"], encoder_lengths=x["encoder_lengths"]
                )
            else:
                loss = self.loss(prediction, y)

            loss = loss * (1 + monotinicity_loss)
        else:
            out = self(x)
            out["prediction"] = self.transform_output(out)

            # calculate loss
            prediction = out["prediction"]
            if isinstance(self.loss, MASE):
                loss = self.loss(
                    prediction, y, encoder_target=x["encoder_target"], encoder_lengths=x["encoder_lengths"]
                )
            else:
                loss = self.loss(prediction, y)

        # logging losses
        y_hat_detached = prediction.detach()
        y_hat_point_detached = self.loss.to_prediction(y_hat_detached)
        for metric in self.logging_metrics:
            if isinstance(metric, MASE):
                loss_value = metric(
                    y_hat_point_detached, y, encoder_target=x["encoder_target"], encoder_lengths=x["encoder_lengths"]
                )
            else:
                loss_value = metric(y_hat_point_detached, y)
            self.log(f"{label}_{metric.name}", loss_value, on_step=label == "train", on_epoch=True)
        log = {"loss": loss, "n_samples": x["decoder_lengths"].size(0)}
        if self.log_interval(label == "train") > 0:
            self._log_prediction(x, out, batch_idx, label=label)
        return log, out