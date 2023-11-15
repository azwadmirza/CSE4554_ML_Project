    def __init__(self):
        # keep a set of resolved discriminators to test against to ensure
        # that a new action does not conflict with something already executed
        self.resolved_ainfos = {}

        # actions left over from a previous iteration
        self.remaining_actions = []

        # after executing an action we memoize its order to avoid any new
        # actions sending us backward
        self.min_order = None

        # unique tracks the index of the action so we need it to increase
        # monotonically across invocations to resolveConflicts
        self.start = 0