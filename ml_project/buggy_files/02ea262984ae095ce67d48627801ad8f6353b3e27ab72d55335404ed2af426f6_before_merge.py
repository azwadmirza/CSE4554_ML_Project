    def __setup_node_storage(self, node_storage=None) -> None:
        if self.dev_mode:
            node_storage = ForgetfulNodeStorage(registry=self.registry, federated_only=self.federated_only)
        else:
            node_storage = LocalFileBasedNodeStorage(registry=self.registry,
                                                     config_root=self.config_root,
                                                     federated_only=self.federated_only)
        self.node_storage = node_storage