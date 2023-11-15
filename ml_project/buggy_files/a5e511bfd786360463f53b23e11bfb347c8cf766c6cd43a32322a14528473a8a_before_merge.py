    def __init__(self, names):
        # type: (List[str]) -> None
        self.base_packages = set()  # type: Set[str]
        for n in names:
            # Convert module names:
            #     ['a.b.c', 'd.e']
            # to a set of base packages:
            #     set(['a', 'd'])
            self.base_packages.add(n.split('.')[0])
        self.mocked_modules = []  # type: List[str]
        self.orig_meta_path = sys.meta_path
        # enable hook by adding itself to meta_path
        sys.meta_path = sys.meta_path + [self]