    def start_container(self, container, use_network_aliases=True):
        self.connect_container_to_networks(container, use_network_aliases)
        try:
            container.start()
        except APIError as ex:
            if "driver failed programming external connectivity" in ex.explanation:
                log.warn("Host is already in use by another container")
            raise OperationFailedError("Cannot start service %s: %s" % (self.name, ex.explanation))
        return container