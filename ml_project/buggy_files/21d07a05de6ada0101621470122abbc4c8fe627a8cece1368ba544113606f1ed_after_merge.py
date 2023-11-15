    def __init__(self, bot, loop=None, storage: typing.Optional[BaseStorage] = None,
                 run_tasks_by_default: bool = False,
                 throttling_rate_limit=DEFAULT_RATE_LIMIT, no_throttle_error=False,
                 filters_factory=None):

        if not isinstance(bot, Bot):
            raise TypeError(f"Argument 'bot' must be an instance of Bot, not '{type(bot).__name__}'")

        if storage is None:
            storage = DisabledStorage()
        if filters_factory is None:
            filters_factory = FiltersFactory(self)

        self.bot: Bot = bot
        if loop is not None:
            _ensure_loop(loop)
        self._main_loop = loop
        self.storage = storage
        self.run_tasks_by_default = run_tasks_by_default

        self.throttling_rate_limit = throttling_rate_limit
        self.no_throttle_error = no_throttle_error

        self.filters_factory: FiltersFactory = filters_factory
        self.updates_handler = Handler(self, middleware_key='update')
        self.message_handlers = Handler(self, middleware_key='message')
        self.edited_message_handlers = Handler(self, middleware_key='edited_message')
        self.channel_post_handlers = Handler(self, middleware_key='channel_post')
        self.edited_channel_post_handlers = Handler(self, middleware_key='edited_channel_post')
        self.inline_query_handlers = Handler(self, middleware_key='inline_query')
        self.chosen_inline_result_handlers = Handler(self, middleware_key='chosen_inline_result')
        self.callback_query_handlers = Handler(self, middleware_key='callback_query')
        self.shipping_query_handlers = Handler(self, middleware_key='shipping_query')
        self.pre_checkout_query_handlers = Handler(self, middleware_key='pre_checkout_query')
        self.poll_handlers = Handler(self, middleware_key='poll')
        self.poll_answer_handlers = Handler(self, middleware_key='poll_answer')
        self.errors_handlers = Handler(self, once=False, middleware_key='error')

        self.middleware = MiddlewareManager(self)

        self.updates_handler.register(self.process_update)

        self._polling = False
        self._closed = True
        self._dispatcher_close_waiter = None

        self._setup_filters()