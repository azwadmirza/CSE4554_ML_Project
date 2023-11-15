    def check_mappings(intent_properties):
        """Check whether intent-action mappings use proper action names."""

        incorrect = list()
        for intent, properties in intent_properties.items():
            if "triggers" in properties:
                if properties.get("triggers") not in domain.action_names:
                    incorrect.append((intent, properties["triggers"]))
        return incorrect