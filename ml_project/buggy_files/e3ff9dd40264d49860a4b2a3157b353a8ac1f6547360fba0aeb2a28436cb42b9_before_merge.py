    def parse(self, text):
        # type: (basestring) -> dict
        """Parse the input text, classify it and return an object containing its intent and entities."""

        current_context = self.context.copy()

        current_context.update({
            "text": text,
        })

        for component in self.pipeline:
            try:
                args = rasa_nlu.components.fill_args(component.process_args(), current_context, self.config)
                updates = component.process(*args)
                if updates:
                    current_context.update(updates)
            except rasa_nlu.components.MissingArgumentError as e:
                raise Exception("Failed to parse at component '{}'. {}".format(component.name, e.message))

        result = self.default_output_attributes.copy()
        all_attributes = list(self.default_output_attributes.keys()) + self.output_attributes
        # Ensure only keys of `all_attributes` are present and no other keys are returned
        result.update({key: current_context[key] for key in all_attributes if key in current_context})
        return result