    def _parse_body(self, stream):
        rows, cols, entries, format, field, symm = (self.rows, self.cols,
            self.entries, self.format, self.field, self.symmetry)

        try:
            from scipy.sparse import coo_matrix
        except ImportError:
            coo_matrix = None

        dtype = self.DTYPES_BY_FIELD.get(field, None)

        has_symmetry = self.has_symmetry
        is_complex = field == self.FIELD_COMPLEX
        is_skew = symm == self.SYMMETRY_SKEW_SYMMETRIC
        is_herm = symm == self.SYMMETRY_HERMITIAN
        is_pattern = field == self.FIELD_PATTERN

        if format == self.FORMAT_ARRAY:
            a = zeros((rows,cols), dtype=dtype)
            line = 1
            i,j = 0,0
            while line:
                line = stream.readline()
                if not line or line.startswith(b'%'):
                    continue
                if is_complex:
                    aij = complex(*map(float,line.split()))
                else:
                    aij = float(line)
                a[i,j] = aij
                if has_symmetry and i != j:
                    if is_skew:
                        a[j,i] = -aij
                    elif is_herm:
                        a[j,i] = conj(aij)
                    else:
                        a[j,i] = aij
                if i < rows-1:
                    i = i + 1
                else:
                    j = j + 1
                    if not has_symmetry:
                        i = 0
                    else:
                        i = j
            if not (i in [0,j] and j == cols):
                raise ValueError("Parse error, did not read all lines.")

        elif format == self.FORMAT_COORDINATE and coo_matrix is None:
            # Read sparse matrix to dense when coo_matrix is not available.
            a = zeros((rows,cols), dtype=dtype)
            line = 1
            k = 0
            while line:
                line = stream.readline()
                if not line or line.startswith(b'%'):
                    continue
                l = line.split()
                i,j = map(int,l[:2])
                i,j = i-1,j-1
                if is_complex:
                    aij = complex(*map(float,l[2:]))
                else:
                    aij = float(l[2])
                a[i,j] = aij
                if has_symmetry and i != j:
                    if is_skew:
                        a[j,i] = -aij
                    elif is_herm:
                        a[j,i] = conj(aij)
                    else:
                        a[j,i] = aij
                k = k + 1
            if not k == entries:
                ValueError("Did not read all entries")

        elif format == self.FORMAT_COORDINATE:
            # Read sparse COOrdinate format

            if entries == 0:
                # empty matrix
                return coo_matrix((rows, cols), dtype=dtype)

            try:
                # fromfile works for normal files
                flat_data = fromfile(stream, sep=' ')
            except:
                # fallback - fromfile fails for some file-like objects
                flat_data = fromstring(stream.read(), sep=' ')

                # TODO use iterator (e.g. xreadlines) to avoid reading
                # the whole file into memory

            if is_pattern:
                flat_data = flat_data.reshape(-1,2)
                I = ascontiguousarray(flat_data[:,0], dtype='intc')
                J = ascontiguousarray(flat_data[:,1], dtype='intc')
                V = ones(len(I), dtype='int8')  # filler
            elif is_complex:
                flat_data = flat_data.reshape(-1,4)
                I = ascontiguousarray(flat_data[:,0], dtype='intc')
                J = ascontiguousarray(flat_data[:,1], dtype='intc')
                V = ascontiguousarray(flat_data[:,2], dtype='complex')
                V.imag = flat_data[:,3]
            else:
                flat_data = flat_data.reshape(-1,3)
                I = ascontiguousarray(flat_data[:,0], dtype='intc')
                J = ascontiguousarray(flat_data[:,1], dtype='intc')
                V = ascontiguousarray(flat_data[:,2], dtype='float')

            I -= 1  # adjust indices (base 1 -> base 0)
            J -= 1

            if has_symmetry:
                mask = (I != J)       # off diagonal mask
                od_I = I[mask]
                od_J = J[mask]
                od_V = V[mask]

                I = concatenate((I,od_J))
                J = concatenate((J,od_I))

                if is_skew:
                    od_V *= -1
                elif is_herm:
                    od_V = od_V.conjugate()

                V = concatenate((V,od_V))

            a = coo_matrix((V, (I, J)), shape=(rows, cols), dtype=dtype)
        else:
            raise NotImplementedError(format)

        return a