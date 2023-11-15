def _request_export_info() -> Tuple[Text, Text, Text]:
    """Request file path and export stories & nlu data to that path"""

    # export training data and quit
    questions = questionary.form(
        export_stories=questionary.text(
            message="Export stories to (if file exists, this "
            "will append the stories)",
            default=PATHS["stories"],
            validate=io_utils.questionary_file_path_validator(
                [".md"],
                "Please provide a valid export path for the stories, e.g. 'stories.md'.",
            ),
        ),
        export_nlu=questionary.text(
            message="Export NLU data to (if file exists, this will "
            "merge learned data with previous training examples)",
            default=PATHS["nlu"],
            validate=io_utils.questionary_file_path_validator(
                [".md"],
                "Please provide a valid export path for the NLU data, e.g. 'nlu.md'.",
            ),
        ),
        export_domain=questionary.text(
            message="Export domain file to (if file exists, this "
            "will be overwritten)",
            default=PATHS["domain"],
            validate=io_utils.questionary_file_path_validator(
                [".yml", ".yaml"],
                "Please provide a valid export path for the domain file, e.g. 'domain.yml'.",
            ),
        ),
    )

    answers = questions.ask()
    if not answers:
        raise Abort()

    return (answers["export_stories"], answers["export_nlu"], answers["export_domain"])