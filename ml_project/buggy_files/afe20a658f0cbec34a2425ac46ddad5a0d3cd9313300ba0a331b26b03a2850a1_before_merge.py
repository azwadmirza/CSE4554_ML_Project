    def to(self, raw: T, of_type: Type[V]) -> V:
        from_module = getattr(of_type, "__module__", None)
        if from_module in ("typing", "typing_extensions"):
            return self._to_typing(raw, of_type)  # type: ignore[return-value]
        elif issubclass(of_type, Path):
            return self.to_path(raw)  # type: ignore[return-value]
        elif issubclass(of_type, bool):
            return self.to_bool(raw)  # type: ignore[return-value]
        elif issubclass(of_type, Command):
            return self.to_command(raw)  # type: ignore[return-value]
        elif issubclass(of_type, EnvList):
            return self.to_env_list(raw)  # type: ignore[return-value]
        elif issubclass(of_type, str):
            return self.to_str(raw)  # type: ignore[return-value]
        elif isinstance(raw, of_type):
            return raw
        elif issubclass(of_type, Enum):
            return cast(V, getattr(of_type, str(raw)))
        return of_type(raw)  # type: ignore[call-arg]