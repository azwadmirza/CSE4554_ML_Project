    def __init__(self,
                 entry_points,
                 states,
                 fallbacks,
                 allow_reentry=False,
                 per_chat=True,
                 per_user=True,
                 per_message=False,
                 conversation_timeout=None,
                 name=None,
                 persistent=False,
                 map_to_parent=None):

        self._entry_points = entry_points
        self._states = states
        self._fallbacks = fallbacks

        self._allow_reentry = allow_reentry
        self._per_user = per_user
        self._per_chat = per_chat
        self._per_message = per_message
        self._conversation_timeout = conversation_timeout
        self._name = name
        if persistent and not self.name:
            raise ValueError("Conversations can't be persistent when handler is unnamed.")
        self.persistent = persistent
        self._persistence = None
        """:obj:`telegram.ext.BasePersistence`: The persistence used to store conversations.
        Set by dispatcher"""
        self._map_to_parent = map_to_parent

        self.timeout_jobs = dict()
        self._timeout_jobs_lock = Lock()
        self._conversations = dict()
        self._conversations_lock = Lock()

        self.logger = logging.getLogger(__name__)

        if not any((self.per_user, self.per_chat, self.per_message)):
            raise ValueError("'per_user', 'per_chat' and 'per_message' can't all be 'False'")

        if self.per_message and not self.per_chat:
            warnings.warn("If 'per_message=True' is used, 'per_chat=True' should also be used, "
                          "since message IDs are not globally unique.")

        all_handlers = list()
        all_handlers.extend(entry_points)
        all_handlers.extend(fallbacks)

        for state_handlers in states.values():
            all_handlers.extend(state_handlers)

        if self.per_message:
            for handler in all_handlers:
                if not isinstance(handler, CallbackQueryHandler):
                    warnings.warn("If 'per_message=True', all entry points and state handlers"
                                  " must be 'CallbackQueryHandler', since no other handlers "
                                  "have a message context.")
                    break
        else:
            for handler in all_handlers:
                if isinstance(handler, CallbackQueryHandler):
                    warnings.warn("If 'per_message=False', 'CallbackQueryHandler' will not be "
                                  "tracked for every message.")
                    break

        if self.per_chat:
            for handler in all_handlers:
                if isinstance(handler, (InlineQueryHandler, ChosenInlineResultHandler)):
                    warnings.warn("If 'per_chat=True', 'InlineQueryHandler' can not be used, "
                                  "since inline queries have no chat context.")
                    break