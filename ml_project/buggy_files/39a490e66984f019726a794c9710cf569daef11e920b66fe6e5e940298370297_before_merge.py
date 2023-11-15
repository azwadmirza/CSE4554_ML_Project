    def train_entity_extractor(self, entity_examples):
        trainer = ner_trainer(self.fe_file)
        for example in entity_examples:
            tokens = tokenize(example["text"])
            sample = ner_training_instance(tokens)
            for ent in example["entities"]:
                _slice = example["text"][ent["start"]:ent["end"]]
                val_tokens = tokenize(_slice)
                start, end = self.start_and_end(tokens, val_tokens)
                sample.add_entity(xrange(start, end), ent["entity"])
            trainer.add(sample)

        ner = trainer.train()
        return ner