    def __init__(self, exchange_name: str, config: dict) -> None:
        """
        Load the custom class from config parameter
        :param config: configuration dictionary
        """
        exchange_name = exchange_name.title()
        try:
            self.exchange = self._load_exchange(exchange_name, kwargs={'config': config})
        except ImportError:
            logger.info(
                f"No {exchange_name} specific subclass found. Using the generic class instead.")
            self.exchange = Exchange(config)