    def __init__(self, name: str, permutation: Union[List[Union[int, np.int_]], np.ndarray]):
        if not isinstance(name, str):
            raise TypeError("Gate name must be a string")

        if name in RESERVED_WORDS:
            raise ValueError(
                "Cannot use {} for a gate name since it's a reserved word".format(name)
            )

        if isinstance(permutation, list):
            elts = len(permutation)
        elif isinstance(permutation, np.ndarray):
            elts, cols = permutation.shape
            if cols != 1:
                raise ValueError("Permutation must have shape (N, 1)")
        else:
            raise ValueError("Permutation must be a list or NumPy array")

        if 0 != elts & (elts - 1):
            raise ValueError("Dimension of permutation must be a power of 2, got {0}".format(elts))

        self.name = name
        self.permutation = np.asarray(permutation)
        self.parameters = None