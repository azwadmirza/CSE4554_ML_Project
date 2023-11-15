    def train_entity_extractor(self, entity_examples):
        trainer = ner_trainer(self.fe_file)
        for example in entity_examples:
            tokens = tokenize(example["text"])
            sample = ner_training_instance(tokens)
            for ent in example["entities"]:
                _slice = example["text"][ent["start"]:ent["end"]]
                val_tokens = tokenize(_slice)
                entity_location = self.find_location_of_entity(tokens, val_tokens)
                if entity_location:
                    sample.add_entity(xrange(entity_location[0], entity_location[1]), ent["entity"])
                else:
                    logging.warn("Ignored invalid entity example. Make sure indices are correct. " +
                                 "Text: \"{}\", Invalid entity: \"{}\".".format(example["text"], _slice))
            trainer.add(sample)

        ner = trainer.train()
        return ner