    def plot_prediction(
        self,
        x: Dict[str, torch.Tensor],
        out: Dict[str, torch.Tensor],
        idx: int = 0,
        add_loss_to_title: Union[Metric, torch.Tensor, bool] = False,
        show_future_observed: bool = True,
        ax=None,
    ) -> plt.Figure:
        """
        Plot prediction of prediction vs actuals

        Args:
            x: network input
            out: network output
            idx: index of prediction to plot
            add_loss_to_title: if to add loss to title or loss function to calculate. Can be either metrics,
                bool indicating if to use loss metric or tensor which contains losses for all samples. Default to False.
            show_future_observed: if to show actuals for future. Defaults to True.
            ax: matplotlib axes to plot on

        Returns:
            matplotlib figure
        """
        # all true values for y of the first sample in batch
        y_all = torch.cat([x["encoder_target"][idx], x["decoder_target"][idx]])
        if y_all.ndim == 2:  # timesteps, (target, weight), i.e. weight is included
            y_all = y_all[:, 0]
        max_encoder_length = x["encoder_lengths"].max()
        y = torch.cat(
            (
                y_all[: x["encoder_lengths"][idx]],
                y_all[max_encoder_length : (max_encoder_length + x["decoder_lengths"][idx])],
            ),
        )
        # get predictions
        y_pred = out["prediction"].detach().cpu()
        y_hat = y_pred[idx, : x["decoder_lengths"][idx]]

        # move to cpu
        y = y.detach().cpu()
        # create figure
        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.get_figure()
        n_pred = y_hat.shape[0]
        x_obs = np.arange(-(y.shape[0] - n_pred), 0)
        x_pred = np.arange(n_pred)
        prop_cycle = iter(plt.rcParams["axes.prop_cycle"])
        obs_color = next(prop_cycle)["color"]
        pred_color = next(prop_cycle)["color"]
        # plot observed history
        if len(x_obs) > 0:
            if len(x_obs) > 1:
                plotter = ax.plot
            else:
                plotter = ax.scatter
            plotter(x_obs, y[:-n_pred], label="observed", c=obs_color)
        if len(x_pred) > 1:
            plotter = ax.plot
        else:
            plotter = ax.scatter

        # plot observed prediction
        if show_future_observed:
            plotter(x_pred, y[-n_pred:], label=None, c=obs_color)

        # plot prediction
        plotter(x_pred, self.loss.to_prediction(y_hat.unsqueeze(0))[0], label="predicted", c=pred_color)

        # plot predicted quantiles
        y_quantiles = self.loss.to_quantiles(y_hat.unsqueeze(0))[0]
        plotter(x_pred, y_quantiles[:, y_quantiles.shape[1] // 2], c=pred_color, alpha=0.15)
        for i in range(y_quantiles.shape[1] // 2):
            if len(x_pred) > 1:
                ax.fill_between(x_pred, y_quantiles[:, i], y_quantiles[:, -i - 1], alpha=0.15, fc=pred_color)
            else:
                quantiles = torch.tensor([[y_quantiles[0, i]], [y_quantiles[0, -i - 1]]])
                ax.errorbar(
                    x_pred,
                    y[[-n_pred]],
                    yerr=quantiles - y[-n_pred],
                    c=pred_color,
                    capsize=1.0,
                )
        if add_loss_to_title is not False:
            if isinstance(add_loss_to_title, bool):
                loss = self.loss
            elif isinstance(add_loss_to_title, torch.Tensor):
                loss = add_loss_to_title.detach()[idx].item()
            elif isinstance(add_loss_to_title, Metric):
                loss = add_loss_to_title
                loss.quantiles = self.loss.quantiles
            else:
                raise ValueError(f"add_loss_to_title '{add_loss_to_title}'' is unkown")
            if isinstance(loss, MASE):
                loss_value = loss(y_hat[None], y[-n_pred:][None], y[:n_pred][None])
            elif isinstance(loss, Metric):
                loss_value = loss(y_hat[None], y[-n_pred:][None])
            else:
                loss_value = loss
            ax.set_title(f"Loss {loss_value:.3g}")
        ax.set_xlabel("Time index")
        fig.legend()
        return fig