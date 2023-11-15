    def train(self, data: TrainingData, **kwargs: Any) -> "Interpreter":
        """Trains the underlying pipeline using the provided training data."""

        self.training_data = data

        self.training_data.validate()

        context = kwargs

        for component in self.pipeline:
            updates = component.provide_context()
            if updates:
                context.update(updates)

        # Before the training starts: check that all arguments are provided
        if not self.skip_validation:
            components.validate_required_components_from_data(
                self.pipeline, self.training_data
            )

        # data gets modified internally during the training - hence the copy
        working_data: TrainingData = copy.deepcopy(data)

        for i, component in enumerate(self.pipeline):
            if isinstance(component, (EntityExtractor, IntentClassifier)):
                working_data = working_data.without_empty_e2e_examples()

            logger.info(f"Starting to train component {component.name}")
            component.prepare_partial_processing(self.pipeline[:i], context)
            updates = component.train(working_data, self.config, **context)
            logger.info("Finished training component.")
            if updates:
                context.update(updates)

        return Interpreter(self.pipeline, context)