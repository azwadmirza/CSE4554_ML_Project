async def _get_existing_models(config):
    """Get a list of models already trained in the Rasa NLU project."""
    project = config.get("project", RASANLU_DEFAULT_PROJECT)
    async with aiohttp.ClientSession() as session:
        try:
            resp = await session.get(await _build_status_url(config))
            if resp.status == 200:
                result = await resp.json()
                if project in result["available_projects"]:
                    project_models = result["available_projects"][project]
                    return project_models["available_models"]
        except aiohttp.ClientOSError:
            pass
    return []