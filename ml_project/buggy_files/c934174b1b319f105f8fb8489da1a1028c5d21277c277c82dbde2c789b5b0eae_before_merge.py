async def _write_nlu_to_file(
    export_nlu_path: Text, events: List[Dict[Text, Any]]
) -> None:
    """Write the nlu data of the sender_id to the file paths."""
    from rasa.nlu.training_data import TrainingData

    msgs = _collect_messages(events)

    # noinspection PyBroadException
    try:
        previous_examples = loading.load_data(export_nlu_path)
    except Exception as e:
        logger.exception("An exception occurred while trying to load the NLU data.")

        export_nlu_path = questionary.text(
            message="Could not load existing NLU data, please "
            "specify where to store NLU data learned in "
            "this session (this will overwrite any "
            "existing file). {}".format(str(e)),
            default=PATHS["backup"],
        ).ask()

        if export_nlu_path is None:
            return

        previous_examples = TrainingData()

    nlu_data = previous_examples.merge(TrainingData(msgs))

    # need to guess the format of the file before opening it to avoid a read
    # in a write
    if loading.guess_format(export_nlu_path) in {"md", "unk"}:
        fformat = "md"
    else:
        fformat = "json"

    with open(export_nlu_path, "w", encoding="utf-8") as f:
        if fformat == "md":
            f.write(nlu_data.as_markdown())
        else:
            f.write(nlu_data.as_json())