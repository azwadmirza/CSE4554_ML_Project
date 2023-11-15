    def _calculate_statistics(self):
        """ Calculate and log simple summary statistics of the datasets """
        logger.info("")
        logger.info("DATASETS SUMMARY")
        logger.info("================")

        self.counts = {}

        if self.data["train"]:
            self.counts["train"] = len(self.data["train"])
            if "input_ids" in self.tensor_names:
                clipped, ave_len, seq_lens, max_seq_len = self._calc_length_stats_single_encoder()
            elif "query_input_ids" in self.tensor_names and "passage_input_ids" in self.tensor_names:
                clipped, ave_len, seq_lens, max_seq_len = self._calc_length_stats_biencoder()
            else:
                logger.warning(f"Could not compute length statistics because 'input_ids' or 'query_input_ids' and 'passage_input_ids' are missing.")
                clipped = -1
                ave_len = -1
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


        logger.info("Examples in train: {}".format(self.counts["train"]))
        logger.info("Examples in dev  : {}".format(self.counts["dev"]))
        logger.info("Examples in test : {}".format(self.counts["test"]))
        logger.info("")
        if self.data["train"]:
            if "input_ids" in self.tensor_names:
                logger.info("Longest sequence length observed after clipping:     {}".format(max(seq_lens)))
                logger.info("Average sequence length after clipping: {}".format(ave_len))
                logger.info("Proportion clipped:      {}".format(clipped))
                if clipped > 0.5:
                    logger.info("[Farmer's Tip] {}% of your samples got cut down to {} tokens. "
                                "Consider increasing max_seq_len. "
                                "This will lead to higher memory consumption but is likely to "
                                "improve your model performance".format(round(clipped * 100, 1), max_seq_len))
            elif "query_input_ids" in self.tensor_names and "passage_input_ids" in self.tensor_names:
                logger.info("Longest query length observed after clipping: {}   - for max_query_len: {}".format(max(seq_lens[0]),max_seq_len[0]))
                logger.info("Average query length after clipping:          {}".format(ave_len[0]))
                logger.info("Proportion queries clipped:                   {}".format(clipped[0]))
                logger.info("")
                logger.info("Longest passage length observed after clipping: {}   - for max_passage_len: {}".format(max(seq_lens[1]),max_seq_len[1]))
                logger.info("Average passage length after clipping:          {}".format(ave_len[1]))
                logger.info("Proportion passages clipped:                    {}".format(clipped[1]))

        MlLogger.log_params(
            {
                "n_samples_train": self.counts["train"],
                "n_samples_dev": self.counts["dev"],
                "n_samples_test": self.counts["test"],
                "batch_size": self.batch_size,
                "ave_seq_len": ave_len,
                "clipped": clipped,
            }
        )