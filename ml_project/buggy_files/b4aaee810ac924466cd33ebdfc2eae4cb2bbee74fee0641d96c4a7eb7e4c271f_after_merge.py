    def refresh_partial(self, node: Union[MypyFile, FuncDef, OverloadedFuncDef],
                        patches: List[Tuple[int, Callable[[], None]]]) -> None:
        """Refresh a stale target in fine-grained incremental mode."""
        self.options = self.sem.options
        self.patches = patches
        if isinstance(node, MypyFile):
            self.recurse_into_functions = False
            self.refresh_top_level(node)
        else:
            self.recurse_into_functions = True
            self.accept(node)
        self.patches = []