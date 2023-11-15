            def patch() -> None:
                self.perform_transform(node,
                    lambda tp: tp.accept(TypeVariableChecker(self.fail)))