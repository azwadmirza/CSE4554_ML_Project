    def __init__(self, inpt=None, dims=[[], []], shape=[],
                 type=None, isherm=None, fast=False, superrep=None):
        """
        Qobj constructor.
        """
        self._isherm = None

        if fast == 'mc':
            # fast Qobj construction for use in mcsolve with ket output
            self.data = sp.csr_matrix(inpt, dtype=complex)
            self.dims = dims
            self.shape = shape
            self._isherm = False
            self.type = 'ket'
            return

        if fast == 'mc-dm':
            # fast Qobj construction for use in mcsolve with dm output
            self.data = sp.csr_matrix(inpt, dtype=complex)
            self.dims = dims
            self.shape = shape
            self._isherm = True
            self.type = 'oper'
            return

        if isinstance(inpt, Qobj):
            # if input is already Qobj then return identical copy

            # make sure matrix is sparse (safety check)
            self.data = sp.csr_matrix(inpt.data, dtype=complex)

            if not np.any(dims):
                # Dimensions of quantum object used for keeping track of tensor
                # components
                self.dims = inpt.dims
            else:
                self.dims = dims

            if not np.any(shape):
                # Shape of undelying quantum obejct data matrix
                self.shape = inpt.shape
            else:
                self.shape = shape

        elif inpt is None:
            # initialize an empty Qobj with correct dimensions and shape

            if any(dims):
                N, M = np.prod(dims[0]), np.prod(dims[1])
                self.dims = dims

            elif shape:
                N, M = shape
                self.dims = [[N], [M]]

            else:                
                N, M = 1, 1
                self.dims = [[N], [M]]

            self.shape = [N, M]
            self.data = sp.csr_matrix((N, M), dtype=complex)

        elif isinstance(inpt, list) or isinstance(inpt, tuple):
            # case where input is a list
            if len(np.array(inpt).shape) == 1:
                # if list has only one dimension (i.e [5,4])
                inpt = np.array([inpt]).transpose()
            else:  # if list has two dimensions (i.e [[5,4]])
                inpt = np.array(inpt)

            self.data = sp.csr_matrix(inpt, dtype=complex)

            if not np.any(dims):
                self.dims = [[int(inpt.shape[0])], [int(inpt.shape[1])]]
            else:
                self.dims = dims

            if not np.any(shape):
                self.shape = [int(inpt.shape[0]), int(inpt.shape[1])]
            else:
                self.shape = shape

        elif isinstance(inpt, np.ndarray) or sp.issparse(inpt):
            # case where input is array or sparse
            if inpt.ndim == 1:
                inpt = inpt[:, np.newaxis]

            self.data = sp.csr_matrix(inpt, dtype=complex)

            if not np.any(dims):
                self.dims = [[int(inpt.shape[0])], [int(inpt.shape[1])]]
            else:
                self.dims = dims

            if not np.any(shape):
                self.shape = [int(inpt.shape[0]), int(inpt.shape[1])]
            else:
                self.shape = shape
            
        elif isinstance(inpt, (int, float, complex, np.int64)):
            # if input is int, float, or complex then convert to array
            self.data = sp.csr_matrix([[inpt]], dtype=complex)

            if not np.any(dims):
                self.dims = [[1], [1]]
            else:
                self.dims = dims

            if not np.any(shape):
                self.shape = [1, 1]
            else:
                self.shape = shape

        else:
            warnings.warn("Initializing Qobj from unsupported type")
            inpt = np.array([[0]])
            self.data = sp.csr_matrix(inpt, dtype=complex)
            self.dims = [[int(inpt.shape[0])], [int(inpt.shape[1])]]
            self.shape = [int(inpt.shape[0]), int(inpt.shape[1])]

        # Signifies if quantum object corresponds to Hermitian operator
        if isherm is None:
            if qset.auto_herm:
                self._isherm = self.isherm
            else:
                self._isherm = None
        else:
            self._isherm = isherm

        # Signifies if quantum object corresponds to a ket, bra, operator, or
        # super-operator
        if type is None:
            self.type = _typecheck(self)
        else:
            self.type = type
            
        if self.type == 'super':
            self.superrep = superrep if superrep else 'super'
        else:
            self.superrep = None