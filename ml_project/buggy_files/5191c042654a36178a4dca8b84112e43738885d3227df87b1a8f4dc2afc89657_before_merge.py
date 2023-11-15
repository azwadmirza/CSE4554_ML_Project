    def refresh_partial(self, node: Union[MypyFile, FuncItem, OverloadedFuncDef],
                        patches: List[Tuple[int, Callable[[], None]]]) -> None:
        """Refresh a stale target in fine-grained incremental mode."""
        self.patches = patches
        if isinstance(node, MypyFile):
            self.refresh_top_level(node)
        else:
            self.recurse_into_functions = True
            self.accept(node)
        del self.patches