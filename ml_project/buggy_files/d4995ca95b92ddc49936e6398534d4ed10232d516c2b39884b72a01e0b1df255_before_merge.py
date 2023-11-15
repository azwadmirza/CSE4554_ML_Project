async def train_rasanlu(config, skills):
    """Train a Rasa NLU model based on the loaded skills."""
    _LOGGER.info(_("Starting Rasa NLU training."))
    intents = await _get_all_intents(skills)
    if intents is None:
        _LOGGER.warning(_("No intents found, skipping training."))
        return False

    config["model"] = await _get_intents_fingerprint(intents)
    if config["model"] in await _get_existing_models(config):
        _LOGGER.info(_("This model already exists, skipping training..."))
        await _init_model(config)
        return True

    async with aiohttp.ClientSession() as session:
        _LOGGER.info(_("Now training the model. This may take a while..."))

        url = await _build_training_url(config)

        try:
            training_start = arrow.now()
            resp = await session.post(url, data=intents)
        except aiohttp.client_exceptions.ClientConnectorError:
            _LOGGER.error(_("Unable to connect to Rasa NLU, training failed."))
            return False

        if resp.status == 200:
            result = await resp.json()
            if "info" in result and "new model trained" in result["info"]:
                time_taken = (arrow.now() - training_start).total_seconds()
                _LOGGER.info(_("Rasa NLU training completed in %s seconds."),
                             int(time_taken))
                await _init_model(config)
                return True

            _LOGGER.debug(result)

        _LOGGER.error(_("Bad Rasa NLU response - %s"), await resp.text())
        _LOGGER.error(_("Rasa NLU training failed."))
        return False