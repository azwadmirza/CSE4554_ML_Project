    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        # checks whether there is at least one
        # example with an entity annotation
        if not training_data.entity_examples:
            logger.debug(
                "No training examples with entities present. Skip training"
                "of 'CRFEntityExtractor'."
            )
            return

        self.check_correct_entity_annotations(training_data)

        if self.component_config[BILOU_FLAG]:
            bilou_utils.apply_bilou_schema(training_data)

        # only keep the CRFs for tags we actually have training data for
        self._update_crf_order(training_data)

        # filter out pre-trained entity examples
        entity_examples = self.filter_trainable_entities(training_data.nlu_examples)

        dataset = [self._convert_to_crf_tokens(example) for example in entity_examples]

        self._train_model(dataset)