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

        # https://github.com/RasaHQ/rasa_nlu/blob/master/docs/http.rst#post-train
        # Note : The request should always be sent as
        # application/x-yml regardless of wether you use
        # json or md for the data format. Do not send json as
        # application/json for example.+
        headers = {"content-type": "application/x-yml"}

        try:
            training_start = arrow.now()
            resp = await session.post(url, data=intents, headers=headers)
        except aiohttp.client_exceptions.ClientConnectorError:
            _LOGGER.error(_("Unable to connect to Rasa NLU, training failed."))
            return False

        if resp.status == 200:
            if resp.content_type == "application/json":
                result = await resp.json()
                if "info" in result and "new model trained" in result["info"]:
                    time_taken = (arrow.now() - training_start).total_seconds()
                    _LOGGER.info(
                        _("Rasa NLU training completed in %s seconds."), int(time_taken)
                    )
                    await _init_model(config)
                    return True

                _LOGGER.debug(result)
            if (
                resp.content_type == "application/zip"
                and resp.content_disposition.type == "attachment"
            ):
                time_taken = (arrow.now() - training_start).total_seconds()
                _LOGGER.info(
                    _("Rasa NLU training completed in %s seconds."), int(time_taken)
                )
                await _init_model(config)
                """
                As inditated in the issue #886, returned zip file is ignored, this can be changed
                This can be changed in future release if needed
                Saving model.zip file example :
                try:
                    output_file = open("/target/directory/model.zip","wb")
                    data = await resp.read()
                    output_file.write(data)
                    output_file.close()
                    _LOGGER.debug("Rasa taining model file saved to /target/directory/model.zip")
                except:
                    _LOGGER.error("Cannot save rasa taining model file to /target/directory/model.zip")
                """
                return True

        _LOGGER.error(_("Bad Rasa NLU response - %s"), await resp.text())
        _LOGGER.error(_("Rasa NLU training failed."))
        return False