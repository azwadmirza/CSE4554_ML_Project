def _load_and_set_updated_model(
    agent: "Agent", model_directory: Text, fingerprint: Text
) -> None:
    """Load the persisted model into memory and set the model on the agent.

    Args:
        agent: Instance of `Agent` to update with the new model.
        model_directory: Rasa model directory.
        fingerprint: Fingerprint of the supplied model at `model_directory`.
    """
    logger.debug(f"Found new model with fingerprint {fingerprint}. Loading...")

    core_path, nlu_path = get_model_subdirectories(model_directory)

    try:
        interpreter = _load_interpreter(agent, nlu_path)
        domain, policy_ensemble = _load_domain_and_policy_ensemble(core_path)

        agent.update_model(
            domain, policy_ensemble, fingerprint, interpreter, model_directory
        )

        logger.debug("Finished updating agent to new model.")
    except Exception as e:
        logger.exception(
            f"Failed to update model. The previous model will stay loaded instead. "
            f"Error: {e}"
        )