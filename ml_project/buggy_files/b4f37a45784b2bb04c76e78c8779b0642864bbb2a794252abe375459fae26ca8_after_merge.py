    def collect_intent_properties(intent_list):
        intent_properties = {}
        for intent in intent_list:
            if isinstance(intent, dict):
                name = list(intent.keys())[0]
                for properties in intent.values():
                    if "use_entities" not in properties:
                        properties["use_entities"] = True
            else:
                name = intent
                intent = {intent: {"use_entities": True}}

            if name in intent_properties.keys():
                raise InvalidDomain(
                    "Intents are not unique! Found two intents with name '{}'. "
                    "Either rename or remove one of them.".format(name)
                )

            intent_properties.update(intent)
        return intent_properties