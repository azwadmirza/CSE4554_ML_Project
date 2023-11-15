    def __init__(self, context=None, socket_type=DEALER, shadow=None):
        '''Initialize the object and the send and receive state.'''
        if context is None:
            context = self._context_class.instance()
        # There are multiple backends which handle shadow differently.
        # It is best to send it as a positional to avoid problems.
        base = super(_Socket, self)
        if shadow is None:
            base.__init__(context, socket_type)
        else:
            base.__init__(context, socket_type, shadow)
        # Initialize send and receive states, which are mapped as:
        #    state:  -1    0   [  1  ]    2       3       4      5
        #    frame:  VIA  PEER [PROTO] USER_ID  MSG_ID  SUBSYS  ...
        state = -1 if self.type == ROUTER else 0
        object.__setattr__(self, '_send_state', state)
        object.__setattr__(self, '_recv_state', state)
        object.__setattr__(self, '_Socket__local', self._local_class())
        self.immediate = True