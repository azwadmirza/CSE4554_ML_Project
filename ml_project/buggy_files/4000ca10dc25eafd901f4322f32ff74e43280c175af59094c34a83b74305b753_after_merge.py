    def __init__(self, name: str, permutation: Union[List[Union[int, np.int_]], np.ndarray]):
        if not isinstance(name, str):
            raise TypeError("Gate name must be a string")

        if name in RESERVED_WORDS:
            raise ValueError(f"Cannot use {name} for a gate name since it's a reserved word")

        if not isinstance(permutation, (list, np.ndarray)):
            raise ValueError(
                f"Permutation must be a list or NumPy array, got value of type {type(permutation)}"
            )

        permutation = np.asarray(permutation)

        ndim = permutation.ndim
        if 1 != ndim:
            raise ValueError(f"Permutation must have dimension 1, got {permutation.ndim}")

        elts = permutation.shape[0]
        if 0 != elts & (elts - 1):
            raise ValueError(f"Dimension of permutation must be a power of 2, got {elts}")

        self.name = name
        self.permutation = permutation
        self.parameters = None