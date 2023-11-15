    def __init__(self, node, scope_type):
        self._atomic = ScopeConsumer(copy.copy(node.locals), {}, scope_type)
        self.node = node