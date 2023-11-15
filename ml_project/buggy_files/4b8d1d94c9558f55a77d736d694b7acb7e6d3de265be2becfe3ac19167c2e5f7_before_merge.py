    def _calculate_statistics(self):
        """ Calculate and log simple summary statistics of the datasets """
        logger.info("")
        logger.info("DATASETS SUMMARY")
        logger.info("================")

        self.counts = {}

        if self.data["train"]:
            self.counts["train"] = len(self.data["train"])
        else:
            self.counts["train"] = 0

        if self.data["dev"]:
            self.counts["dev"] = len(self.data["dev"])
        else:
            self.counts["dev"] = 0

        if self.data["test"]:
            self.counts["test"] = len(self.data["test"])
        else:
            self.counts["test"] = 0

        seq_lens = []
        if self.data["train"]:
            for dataset in self.data["train"].datasets:
                train_input_numpy = dataset[:][0].numpy()
                seq_lens.extend(np.sum(train_input_numpy != self.processor.tokenizer.pad_token_id, axis=1))
            max_seq_len = dataset[:][0].shape[1]

        self.clipped = np.mean(np.array(seq_lens) == max_seq_len) if seq_lens else 0
        self.ave_len = np.mean(seq_lens) if seq_lens else 0

        logger.info("Examples in train: {}".format(self.counts["train"]))
        logger.info("Examples in dev  : {}".format(self.counts["dev"]))
        logger.info("Examples in test : {}".format(self.counts["test"]))
        logger.info("")
        if self.data["train"]:
            logger.info("Longest sequence length observed after clipping:     {}".format(max(seq_lens)))
            logger.info("Average sequence length after clipping: {}".format(self.ave_len))
            logger.info("Proportion clipped:      {}".format(self.clipped))
            if self.clipped > 0.5:
                logger.info("[Farmer's Tip] {}% of your samples got cut down to {} tokens. "
                            "Consider increasing max_seq_len. "
                            "This will lead to higher memory consumption but is likely to "
                            "improve your model performance".format(round(self.clipped * 100, 1), max_seq_len))

        MlLogger.log_params(
            {
                "n_samples_train": self.counts["train"],
                "n_samples_dev": self.counts["dev"],
                "n_samples_test": self.counts["test"],
                "batch_size": self.batch_size,
                "ave_seq_len": self.ave_len,
                "clipped": self.clipped,
            }
        )