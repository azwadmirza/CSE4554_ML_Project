    def _log_prediction(self, x, out, batch_idx, label="train"):
        # log single prediction figure
        log_interval = self.log_interval(label == "train")
        if (batch_idx % log_interval == 0 or log_interval < 1.0) and log_interval > 0:
            if log_interval < 1.0:  # log multiple steps
                log_indices = torch.arange(
                    0, len(x["encoder_lengths"]), max(1, round(log_interval * len(x["encoder_lengths"])))
                )
            else:
                log_indices = [0]
            for idx in log_indices:
                fig = self.plot_prediction(x, out, idx=idx, add_loss_to_title=True)
                tag = f"{label.capitalize()} prediction"
                if label == "train":
                    tag += f" of item {idx} in global batch {self.global_step}"
                else:
                    tag += f" of item {idx} in batch {batch_idx}"
                self.logger.experiment.add_figure(
                    tag,
                    fig,
                    global_step=self.global_step,
                )