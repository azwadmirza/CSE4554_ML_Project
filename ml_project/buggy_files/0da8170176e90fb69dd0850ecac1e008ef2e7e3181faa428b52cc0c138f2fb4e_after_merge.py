    def start_container(self, container, use_network_aliases=True):
        self.connect_container_to_networks(container, use_network_aliases)
        try:
            container.start()
        except APIError as ex:
            expl = binarystr_to_unicode(ex.explanation)
            if "driver failed programming external connectivity" in expl:
                log.warn("Host is already in use by another container")
            raise OperationFailedError("Cannot start service %s: %s" % (self.name, expl))
        return container