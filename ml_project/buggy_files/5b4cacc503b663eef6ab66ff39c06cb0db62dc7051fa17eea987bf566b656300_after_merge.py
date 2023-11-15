def _pass_config_to_playlist(config: Config, bot: Red):
    global _config, _bot, database
    if _config is None:
        _config = config
    if _bot is None:
        _bot = bot
    if database is None:
        database = PlaylistInterface()