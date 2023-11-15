async def train_async(
    domain: Union[Domain, Text],
    config: Text,
    training_files: Optional[Union[Text, List[Text]]],
    output_path: Text = DEFAULT_MODELS_PATH,
    force_training: bool = False,
    fixed_model_name: Optional[Text] = None,
    kwargs: Optional[Dict] = None,
) -> Optional[Text]:
    """Trains a Rasa model (Core and NLU).

    Args:
        domain: Path to the domain file.
        config: Path to the config for Core and NLU.
        training_files: Paths to the training data for Core and NLU.
        output_path: Output path.
        force_training: If `True` retrain model even if data has not changed.
        fixed_model_name: Name of model to be stored.
        kwargs: Additional training parameters.

    Returns:
        Path of the trained model archive.
    """
    skill_imports = SkillSelector.load(config, training_files)
    try:
        domain = Domain.load(domain, skill_imports)
        domain.check_missing_templates()
    except InvalidDomain:
        domain = None

    story_directory, nlu_data_directory = data.get_core_nlu_directories(
        training_files, skill_imports
    )

    with ExitStack() as stack:
        train_path = stack.enter_context(TempDirectoryPath(tempfile.mkdtemp()))
        nlu_data = stack.enter_context(TempDirectoryPath(nlu_data_directory))
        story = stack.enter_context(TempDirectoryPath(story_directory))

        if domain is None:
            return handle_domain_if_not_exists(
                config, nlu_data_directory, output_path, fixed_model_name
            )

        return await _train_async_internal(
            domain,
            config,
            train_path,
            nlu_data,
            story,
            output_path,
            force_training,
            fixed_model_name,
            kwargs,
        )

    if domain is None:
        return handle_domain_if_not_exists(
            config, nlu_data_directory, output_path, fixed_model_name
        )