    def __init__(self,
                 bot,
                 update_queue,
                 workers=4,
                 exception_event=None,
                 job_queue=None,
                 persistence=None,
                 use_context=False):
        self.bot = bot
        self.update_queue = update_queue
        self.job_queue = job_queue
        self.workers = workers
        self.use_context = use_context

        if not use_context:
            warnings.warn('Old Handler API is deprecated - see https://git.io/fxJuV for details',
                          TelegramDeprecationWarning, stacklevel=3)

        self.user_data = defaultdict(dict)
        self.chat_data = defaultdict(dict)
        self.bot_data = {}
        if persistence:
            if not isinstance(persistence, BasePersistence):
                raise TypeError("persistence should be based on telegram.ext.BasePersistence")
            self.persistence = persistence
            if self.persistence.store_user_data:
                self.user_data = self.persistence.get_user_data()
                if not isinstance(self.user_data, defaultdict):
                    raise ValueError("user_data must be of type defaultdict")
            if self.persistence.store_chat_data:
                self.chat_data = self.persistence.get_chat_data()
                if not isinstance(self.chat_data, defaultdict):
                    raise ValueError("chat_data must be of type defaultdict")
            if self.persistence.store_bot_data:
                self.bot_data = self.persistence.get_bot_data()
                if not isinstance(self.bot_data, dict):
                    raise ValueError("bot_data must be of type dict")
        else:
            self.persistence = None

        self.handlers = {}
        """Dict[:obj:`int`, List[:class:`telegram.ext.Handler`]]: Holds the handlers per group."""
        self.groups = []
        """List[:obj:`int`]: A list with all groups."""
        self.error_handlers = []
        """List[:obj:`callable`]: A list of errorHandlers."""

        self.running = False
        """:obj:`bool`: Indicates if this dispatcher is running."""
        self.__stop_event = Event()
        self.__exception_event = exception_event or Event()
        self.__async_queue = Queue()
        self.__async_threads = set()

        # For backward compatibility, we allow a "singleton" mode for the dispatcher. When there's
        # only one instance of Dispatcher, it will be possible to use the `run_async` decorator.
        with self.__singleton_lock:
            if self.__singleton_semaphore.acquire(blocking=0):
                self._set_singleton(self)
            else:
                self._set_singleton(None)