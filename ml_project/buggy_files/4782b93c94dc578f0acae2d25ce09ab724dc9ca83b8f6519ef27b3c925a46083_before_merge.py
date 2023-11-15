    def __init__(self, node):
        self._node = node
        self._enqueued_contacts = {}
        self._process_lc = node.get_looping_call(self._process)