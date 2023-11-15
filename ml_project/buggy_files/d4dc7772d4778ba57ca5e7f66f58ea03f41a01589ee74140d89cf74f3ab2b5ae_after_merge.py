    async def process_message(
        self,
        request: Request,
        on_new_message: Callable[[UserMessage], Awaitable[Any]],
        text,
        sender_id: Optional[Text],
        metadata: Optional[Dict],
    ) -> Any:
        """Slack retries to post messages up to 3 times based on
        failure conditions defined here:
        https://api.slack.com/events-api#failure_conditions
        """
        retry_reason = request.headers.get(self.retry_reason_header)
        retry_count = request.headers.get(self.retry_num_header)
        if retry_count and retry_reason in self.errors_ignore_retry:
            logger.warning(
                f"Received retry #{retry_count} request from slack"
                f" due to {retry_reason}."
            )

            return response.text(None, status=201, headers={"X-Slack-No-Retry": 1})

        if metadata is not None:
            output_channel = metadata.get("out_channel")
            if self.use_threads:
                thread_id = metadata.get("ts")
            else:
                thread_id = None
        else:
            output_channel = None
            thread_id = None

        try:
            user_msg = UserMessage(
                text,
                self.get_output_channel(output_channel, thread_id),
                sender_id,
                input_channel=self.name(),
                metadata=metadata,
            )

            await on_new_message(user_msg)
        except Exception as e:
            logger.error(f"Exception when trying to handle message.{e}")
            logger.error(str(e), exc_info=True)

        return response.text("")