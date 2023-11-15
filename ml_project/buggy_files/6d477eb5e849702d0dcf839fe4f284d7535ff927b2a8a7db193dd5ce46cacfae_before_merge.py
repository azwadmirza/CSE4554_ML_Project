def _load_and_set_updated_model(
    agent: "Agent", model_directory: Text, fingerprint: Text
):
    """Load the persisted model into memory and set the model on the agent."""

    logger.debug(f"Found new model with fingerprint {fingerprint}. Loading...")

    core_path, nlu_path = get_model_subdirectories(model_directory)

    if nlu_path:
        from rasa.core.interpreter import RasaNLUInterpreter

        interpreter = RasaNLUInterpreter(model_directory=nlu_path)
    else:
        interpreter = (
            agent.interpreter if agent.interpreter is not None else RegexInterpreter()
        )

    domain = None
    if core_path:
        domain_path = os.path.join(os.path.abspath(core_path), DEFAULT_DOMAIN_PATH)
        domain = Domain.load(domain_path)

    try:
        policy_ensemble = None
        if core_path:
            policy_ensemble = PolicyEnsemble.load(core_path)
        agent.update_model(
            domain, policy_ensemble, fingerprint, interpreter, model_directory
        )
        logger.debug("Finished updating agent to new model.")
    except Exception:
        logger.exception(
            "Failed to load policy and update agent. "
            "The previous model will stay loaded instead."
        )