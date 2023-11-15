async def train_core_async(
    domain: Union[Domain, Text],
    config: Text,
    stories: Text,
    output: Text,
    train_path: Optional[Text] = None,
    fixed_model_name: Optional[Text] = None,
    kwargs: Optional[Dict] = None,
) -> Optional[Text]:
    """Trains a Core model.

    Args:
        domain: Path to the domain file.
        config: Path to the config file for Core.
        stories: Path to the Core training data.
        output: Output path.
        train_path: If `None` the model will be trained in a temporary
            directory, otherwise in the provided directory.
        fixed_model_name: Name of model to be stored.
        uncompress: If `True` the model will not be compressed.
        kwargs: Additional training parameters.

    Returns:
        If `train_path` is given it returns the path to the model archive,
        otherwise the path to the directory with the trained model files.

    """

    skill_imports = SkillSelector.load(config, stories)

    try:
        domain = Domain.load(domain, skill_imports)
        domain.check_missing_templates()
    except InvalidDomain:
        print_error(
            "Core training was skipped because no valid domain file was found. "
            "Please specify a valid domain using '--domain' argument or check if the provided domain file exists."
        )
        return None

    train_context = TempDirectoryPath(data.get_core_directory(stories, skill_imports))

    with train_context as story_directory:
        if not os.listdir(story_directory):
            print_error(
                "No stories given. Please provide stories in order to "
                "train a Rasa Core model using the '--stories' argument."
            )
            return

        return await _train_core_with_validated_data(
            domain=domain,
            config=config,
            story_directory=story_directory,
            output=output,
            train_path=train_path,
            fixed_model_name=fixed_model_name,
            kwargs=kwargs,
        )