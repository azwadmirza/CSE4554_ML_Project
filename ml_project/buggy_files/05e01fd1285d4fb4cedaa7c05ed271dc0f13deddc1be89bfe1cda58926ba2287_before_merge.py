    def train(
        self, training_trackers: List[DialogueStateTracker], **kwargs: Any
    ) -> None:
        """Train the policies / policy ensemble using dialogue data from file.

        Args:
            training_trackers: trackers to train on
            **kwargs: additional arguments passed to the underlying ML
                           trainer (e.g. keras parameters)
        """
        if not self.is_ready():
            raise AgentNotReady("Can't train without a policy ensemble.")

        # deprecation tests
        if kwargs.get("featurizer"):
            raise Exception(
                "Passing `featurizer` "
                "to `agent.train(...)` is not supported anymore. "
                "Pass appropriate featurizer directly "
                "to the policy configuration instead. More info "
                "{}/core/migrations.html".format(LEGACY_DOCS_BASE_URL)
            )
        if (
            kwargs.get("epochs")
            or kwargs.get("max_history")
            or kwargs.get("batch_size")
        ):
            raise Exception(
                "Passing policy configuration parameters "
                "to `agent.train(...)` is not supported "
                "anymore. Specify parameters directly in the "
                "policy configuration instead. More info "
                "{}/core/migrations.html".format(LEGACY_DOCS_BASE_URL)
            )

        if isinstance(training_trackers, str):
            # the user most likely passed in a file name to load training
            # data from
            raise Exception(
                "Passing a file name to `agent.train(...)` is "
                "not supported anymore. Rather load the data with "
                "`data = agent.load_data(file_name)` and pass it "
                "to `agent.train(data)`."
            )

        logger.debug("Agent trainer got kwargs: {}".format(kwargs))

        check_domain_sanity(self.domain)

        self.policy_ensemble.train(training_trackers, self.domain, **kwargs)
        self._set_fingerprint()