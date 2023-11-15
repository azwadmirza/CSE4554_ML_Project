    def add_flow(self, flow: "prefect.core.flow.Flow") -> str:
        """
        Method for adding a new flow to this Storage object.

        Args:
            - flow (Flow): a Prefect Flow to add

        Returns:
            - str: the location of the newly added flow in this Storage object
        """
        if flow.name in self:
            raise ValueError(
                'Name conflict: Flow with the name "{}" is already present in this storage.'.format(
                    flow.name
                )
            )
        flow_path = "/root/.prefect/{}.prefect".format(slugify(flow.name))
        self.flows[flow.name] = flow_path
        self._flows[flow.name] = flow  # needed prior to build
        return flow_path