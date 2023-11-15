    def __init__(
        self,
        intent_properties: Dict[Text, Any],
        entities: List[Text],
        slots: List[Slot],
        templates: Dict[Text, Any],
        action_names: List[Text],
        form_names: List[Text],
        store_entities_as_slots: bool = True,
    ) -> None:

        self.intent_properties = intent_properties
        self.entities = entities
        self.form_names = form_names
        self.slots = slots
        self.templates = templates

        # only includes custom actions and utterance actions
        self.user_actions = action_names
        # includes all actions (custom, utterance, default actions and forms)
        self.action_names = (
            action.combine_user_with_default_actions(action_names) + form_names
        )
        self.store_entities_as_slots = store_entities_as_slots

        action.ensure_action_name_uniqueness(self.action_names)