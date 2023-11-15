def _request_export_info() -> Tuple[Text, Text, Text]:
    """Request file path and export stories & nlu data to that path"""

    # export training data and quit
    questions = questionary.form(
        export_stories=questionary.text(
            message="Export stories to (if file exists, this "
            "will append the stories)",
            default=PATHS["stories"],
        ),
        export_nlu=questionary.text(
            message="Export NLU data to (if file exists, this will "
            "merge learned data with previous training examples)",
            default=PATHS["nlu"],
        ),
        export_domain=questionary.text(
            message="Export domain file to (if file exists, this "
            "will be overwritten)",
            default=PATHS["domain"],
        ),
    )

    answers = questions.ask()
    if not answers:
        raise Abort()

    return (answers["export_stories"], answers["export_nlu"], answers["export_domain"])