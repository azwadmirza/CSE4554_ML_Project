    def _register_agent(self) -> str:
        """
        Register this agent with Prefect Cloud and retrieve agent ID

        Returns:
            - The agent ID as a string
        """
        agent_id = self.client.register_agent(
            agent_type=type(self).__name__, name=self.name, labels=self.labels  # type: ignore
        )

        self.logger.debug(f"Agent ID: {agent_id}")

        return agent_id