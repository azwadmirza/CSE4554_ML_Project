    def wrapped_strategy(self):
        if self.__wrapped_strategy is None:
            if not inspect.isfunction(self.__definition):
                raise InvalidArgument(
                    (
                        "Excepted a definition to be a function but got %r of type"
                        " %s instead."
                    )
                    % (self.__definition, type(self.__definition).__name__)
                )
            result = self.__definition()
            if result is self:
                raise InvalidArgument("Cannot define a deferred strategy to be itself")
            if not isinstance(result, SearchStrategy):
                raise InvalidArgument(
                    (
                        "Expected definition to return a SearchStrategy but "
                        "returned %r of type %s"
                    )
                    % (result, type(result).__name__)
                )
            self.__wrapped_strategy = result
            del self.__definition
        return self.__wrapped_strategy