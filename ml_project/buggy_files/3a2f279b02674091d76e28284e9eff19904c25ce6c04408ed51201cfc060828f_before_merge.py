    def _create_dev_from_train(self):
        # TODO checks to ensure dev is loaded the right way
        n_dev = int(self.processor.dev_split * len(self.data["train"]))
        n_train = len(self.data["train"]) - n_dev

        # Todo: Seed
        # if(isinstance(self.data["train"], Dataset)):
        #     train_dataset, dev_dataset = random_split(self.data["train"], [n_train, n_dev])
        # else:
        train_dataset, dev_dataset = self.random_split_ConcatDataset(self.data["train"], lengths=[n_train, n_dev])
        self.data["train"] = train_dataset
        if(len(dev_dataset) > 0):
            self.data["dev"] = dev_dataset
        else:
            logger.warning("No dev set created. Maybe adjust the dev_split parameter or the multiprocessing chunk size")

        logger.info(
            f"Took {len(dev_dataset)} samples out of train set to create dev set (dev split is roughly {self.processor.dev_split})"
        )