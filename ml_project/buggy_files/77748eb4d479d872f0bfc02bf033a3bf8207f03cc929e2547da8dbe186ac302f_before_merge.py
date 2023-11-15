    def __init__(self, session):
        resource.Resource.__init__(self)

        child_handler_dict = {"circuits": DebugCircuitsEndpoint, "open_files": DebugOpenFilesEndpoint,
                              "open_sockets": DebugOpenSocketsEndpoint, "threads": DebugThreadsEndpoint,
                              "cpu_history": DebugCPUHistoryEndpoint, "memory_history": DebugMemoryHistoryEndpoint}

        for path, child_cls in child_handler_dict.iteritems():
            self.putChild(path, child_cls(session))