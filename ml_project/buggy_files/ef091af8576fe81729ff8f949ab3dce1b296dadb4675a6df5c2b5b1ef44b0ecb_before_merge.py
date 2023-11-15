    def __init__(self, tree: Module, filename: str = constants.STDIN) -> None:
        """Creates new checker instance."""
        self.tree = maybe_set_parent(tree)
        self.filename = filename