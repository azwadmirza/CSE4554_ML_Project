async def _write_stories_to_file(
    export_story_path: Text, events: List[Dict[Text, Any]]
) -> None:
    """Write the conversation of the sender_id to the file paths."""

    sub_conversations = _split_conversation_at_restarts(events)

    create_path(export_story_path)

    if os.path.exists(export_story_path):
        append_write = "a"  # append if already exists
    else:
        append_write = "w"  # make a new file if not

    with open(export_story_path, append_write, encoding="utf-8") as f:
        for conversation in sub_conversations:
            parsed_events = rasa.core.events.deserialise_events(conversation)
            s = Story.from_events(parsed_events)
            f.write("\n" + s.as_story_string(flat=True))