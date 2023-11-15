    def process(self, message: Message, **kwargs: Any) -> None:
        """Process an incoming message by computing its tokens and dense features.

        Args:
            message: Incoming message object
        """

        message.set(
            LANGUAGE_MODEL_DOCS[TEXT],
            self._get_docs_for_batch([message], attribute=TEXT, inference_mode=True)[0],
        )