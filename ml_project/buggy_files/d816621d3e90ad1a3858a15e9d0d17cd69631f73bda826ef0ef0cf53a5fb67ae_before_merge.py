    def _process_optional_args(self, optional_args):
        # Define locking method
        self.lock_disable = optional_args.get("lock_disable", False)

        self.enablepwd = optional_args.pop("enable_password", "")
        self.eos_autoComplete = optional_args.pop("eos_autoComplete", None)
        # eos_transport is there for backwards compatibility, transport is the preferred method
        transport = optional_args.get(
            "transport", optional_args.get("eos_transport", "https")
        )
        try:
            self.transport_class = pyeapi.client.TRANSPORTS[transport]
        except KeyError:
            raise ConnectionException("Unknown transport: {}".format(self.transport))
        init_args = inspect.getfullargspec(self.transport_class.__init__)[0]

        init_args.pop(0)  # Remove "self"
        init_args.append("enforce_verification")  # Not an arg for unknown reason

        filter_args = ["host", "username", "password", "timeout", "lock_disable"]

        self.eapi_kwargs = {
            k: v
            for k, v in optional_args.items()
            if k in init_args and k not in filter_args
        }