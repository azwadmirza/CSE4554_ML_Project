    def set_state(state: Any) -> None:
        Singleton._instances = state["instances"]
        BaseContainer._resolvers = deepcopy(state["omegaconf_resolvers"])