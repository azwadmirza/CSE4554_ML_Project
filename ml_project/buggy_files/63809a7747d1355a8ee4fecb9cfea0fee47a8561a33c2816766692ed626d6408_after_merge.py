    def tile(cls, op):
        """
        Use LU decomposition to compute inverse of matrix.
        Given a square matrix A:
        P, L, U = lu(A)
        b_eye is an identity matrix with the same shape as matrix A, then,
        (P * L * U) * A_inv = b_eye
        L * (U * A_inv) = P.T * b_eye
        use `solve_triangular` twice to compute the inverse of matrix A.
        """
        from .lu import lu
        from ..datasource import eye
        from ..base.transpose import TensorTranspose
        from .tensordot import tensordot
        from .solve_triangular import solve_triangular
        in_tensor = op.input

        b_eye = eye(in_tensor.shape[0], chunk_size=in_tensor.nsplits)
        b_eye.single_tiles()

        p, l, u = lu(in_tensor)
        p.single_tiles()

        # transposed p equals to inverse of p
        p_transpose = TensorTranspose(
            dtype=p.dtype, sparse=p.op.sparse, axes=list(range(in_tensor.ndim))[::-1]).new_tensor([p], p.shape)
        p_transpose.single_tiles()

        b = tensordot(p_transpose, b_eye, axes=((p_transpose.ndim - 1,), (b_eye.ndim - 2,)))
        b.single_tiles()

        # as `l` is a lower matrix, `lower=True` should be specified.
        uy = solve_triangular(l, b, lower=True)
        uy.single_tiles()

        a_inv = solve_triangular(u, uy)
        a_inv.single_tiles()
        return [a_inv]