    def collect_intent_properties(intent_list):
        intent_properties = {}
        for intent in intent_list:
            if isinstance(intent, dict):
                for properties in intent.values():
                    if "use_entities" not in properties:
                        properties["use_entities"] = True
                intent_properties.update(intent)
            else:
                intent = {intent: {"use_entities": True}}
                intent_properties.update(intent)
        return intent_properties