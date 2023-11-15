async def _write_domain_to_file(
    domain_path: Text, events: List[Dict[Text, Any]], endpoint: EndpointConfig
) -> None:
    """Write an updated domain file to the file path."""

    create_path(domain_path)

    domain = await retrieve_domain(endpoint)
    old_domain = Domain.from_dict(domain)

    messages = _collect_messages(events)
    actions = _collect_actions(events)
    templates = NEW_TEMPLATES

    # TODO for now there is no way to distinguish between action and form
    collected_actions = list(
        {e["name"] for e in actions if e["name"] not in default_action_names()}
    )

    new_domain = Domain(
        intents=_intents_from_messages(messages),
        entities=_entities_from_messages(messages),
        slots=[],
        templates=templates,
        action_names=collected_actions,
        form_names=[],
    )

    old_domain.merge(new_domain).persist_clean(domain_path)