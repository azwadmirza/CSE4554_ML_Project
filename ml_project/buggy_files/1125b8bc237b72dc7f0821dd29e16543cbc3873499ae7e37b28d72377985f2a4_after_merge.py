    def __init__(self, *args, **kwargs):
        """
        Parameters
        ----------
        token  : str, required. Telegram token
            [default: ${TQDM_TELEGRAM_TOKEN}].
        chat_id  : str, required. Telegram chat ID
            [default: ${TQDM_TELEGRAM_CHAT_ID}].

        See `tqdm.auto.tqdm.__init__` for other parameters.
        """
        if not kwargs.get('disable'):
            kwargs = kwargs.copy()
            self.tgio = TelegramIO(
                kwargs.pop('token', getenv('TQDM_TELEGRAM_TOKEN')),
                kwargs.pop('chat_id', getenv('TQDM_TELEGRAM_CHAT_ID')))
        super(tqdm_telegram, self).__init__(*args, **kwargs)