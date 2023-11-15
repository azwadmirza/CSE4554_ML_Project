    def on_train_begin(self, logs=None):
        self.num_epochs = self.params["epochs"]

        if self.show_overall_progress:
            self.overall_progress_tqdm = self.tqdm(
                desc="Training",
                total=self.num_epochs,
                bar_format=self.overall_bar_format,
                leave=self.leave_overall_progress,
                dynamic_ncols=True,
                unit="epochs",
            )

        # set counting mode
        self.mode = "steps"
        self.total_steps = self.params["steps"]