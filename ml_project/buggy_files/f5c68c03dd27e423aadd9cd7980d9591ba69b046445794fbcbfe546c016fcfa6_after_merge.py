    def get_state() -> Any:
        return {
            "instances": Singleton._instances,
            "omegaconf_resolvers": deepcopy(BaseContainer._resolvers),
        }