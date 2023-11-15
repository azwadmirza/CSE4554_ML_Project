    def __getattr__(self, function_name: str) -> Any:
        if self.abi is None:
            raise NoABIFound(
                "There is no ABI found for this contract.",
            )
        elif not self._functions or len(self._functions) == 0:
            raise NoABIFunctionsFound(
                "The ABI for this contract contains no function definitions. ",
                "Are you sure you provided the correct contract ABI?"
            )
        elif function_name not in set(fn['name'] for fn in self._functions):
            functions_available = ', '.join([fn['name'] for fn in self._functions])
            raise ABIFunctionNotFound(
                "The function '{}' was not found in this contract's ABI. ".format(function_name),
                "Here is a list of all of the function names found: ",
                "{}. ".format(functions_available),
                "Did you mean to call one of those functions?"
            )
        else:
            return super().__getattribute__(function_name)