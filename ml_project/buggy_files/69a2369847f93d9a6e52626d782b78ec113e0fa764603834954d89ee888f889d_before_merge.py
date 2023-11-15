    async def _ask_for_slot(
        self,
        domain: Domain,
        nlg: NaturalLanguageGenerator,
        output_channel: OutputChannel,
        slot_name: Text,
        tracker: DialogueStateTracker,
    ) -> List[Event]:
        logger.debug(f"Request next slot '{slot_name}'")

        action_to_ask_for_next_slot = action.action_from_name(
            self._name_of_utterance(domain, slot_name), None, domain.user_actions
        )
        events_to_ask_for_next_slot = await action_to_ask_for_next_slot.run(
            output_channel, nlg, tracker, domain
        )
        return events_to_ask_for_next_slot