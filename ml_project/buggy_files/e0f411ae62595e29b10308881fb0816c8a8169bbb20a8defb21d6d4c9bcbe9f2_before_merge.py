    def __init__(self, *args, **kwargs):
        """
        Parameters
        ----------
        token  : str, required. Discord token
            [default: ${TQDM_DISCORD_TOKEN}].
        channel_id  : int, required. Discord channel ID
            [default: ${TQDM_DISCORD_CHANNEL_ID}].
        mininterval  : float, optional.
          Minimum of [default: 1.5] to avoid rate limit.

        See `tqdm.auto.tqdm.__init__` for other parameters.
        """
        kwargs = kwargs.copy()
        logging.getLogger("HTTPClient").setLevel(logging.WARNING)
        self.dio = DiscordIO(
            kwargs.pop('token', getenv("TQDM_DISCORD_TOKEN")),
            kwargs.pop('channel_id', getenv("TQDM_DISCORD_CHANNEL_ID")))

        kwargs['mininterval'] = max(1.5, kwargs.get('mininterval', 1.5))
        super(tqdm_discord, self).__init__(*args, **kwargs)