def svd(a, full_matrices=True, compute_uv=True):
    '''Singular Value Decomposition.

    Factorizes the matrix ``a`` as ``u * np.diag(s) * v``, where ``u`` and
    ``v`` are unitary and ``s`` is an one-dimensional array of ``a``'s
    singular values.

    Args:
        a (cupy.ndarray): The input matrix with dimension ``(M, N)``.
        full_matrices (bool): If True, it returns u and v with dimensions
            ``(M, M)`` and ``(N, N)``. Otherwise, the dimensions of u and v
            are respectively ``(M, K)`` and ``(K, N)``, where
            ``K = min(M, N)``.
        compute_uv (bool): If True, it only returns singular values.

    Returns:
        tuple of :class:`cupy.ndarray`:
            A tuple of ``(u, s, v)`` such that ``a = u * np.diag(s) * v``.

    .. seealso:: :func:`numpy.linalg.svd`
    '''
    if not cuda.cusolver_enabled:
        raise RuntimeError('Current cupy only supports cusolver in CUDA 8.0')

    # TODO(Saito): Current implementation only accepts two-dimensional arrays
    util._assert_cupy_array(a)
    util._assert_rank2(a)

    # Cast to float32 or float64
    if a.dtype.char == 'f' or a.dtype.char == 'd':
        dtype = a.dtype.char
    else:
        dtype = numpy.find_common_type((a.dtype.char, 'f'), ()).char

    # Remark 1: gesvd only supports m >= n (WHAT?)
    # Remark 2: gesvd only supports jobu = 'A' and jobvt = 'A'
    # Remark 3: gesvd returns matrix U and V^H
    # Remark 4: Remark 2 is removed since cuda 8.0 (new!)
    n, m = a.shape
    if m >= n:
        x = a.astype(dtype, order='C', copy=False)
        trans_flag = False
    else:
        m, n = a.shape
        x = a.transpose().astype(dtype, order='C', copy=False)
        trans_flag = True
    mn = min(m, n)

    if compute_uv:
        if full_matrices:
            u = cupy.empty((m, m), dtype=dtype)
            vt = cupy.empty((n, n), dtype=dtype)
        else:
            u = cupy.empty((mn, m), dtype=dtype)
            vt = cupy.empty((mn, n), dtype=dtype)
        u_ptr, vt_ptr = u.data.ptr, vt.data.ptr
    else:
        u_ptr, vt_ptr = 0, 0  # Use nullptr
    s = cupy.empty(mn, dtype=dtype)
    handle = device.get_cusolver_handle()
    dev_info = cupy.empty(1, dtype=numpy.int32)
    if compute_uv:
        job = ord('A') if full_matrices else ord('S')
    else:
        job = ord('N')
    if dtype == 'f':
        buffersize = cusolver.sgesvd_bufferSize(handle, m, n)
        workspace = cupy.empty(buffersize, dtype=dtype)
        cusolver.sgesvd(
            handle, job, job, m, n, x.data.ptr, m,
            s.data.ptr, u_ptr, m, vt_ptr, n,
            workspace.data.ptr, buffersize, 0, dev_info.data.ptr)
    else:  # dtype == 'd'
        buffersize = cusolver.dgesvd_bufferSize(handle, m, n)
        workspace = cupy.empty(buffersize, dtype=dtype)
        cusolver.dgesvd(
            handle, job, job, m, n, x.data.ptr, m,
            s.data.ptr, u_ptr, m, vt_ptr, n,
            workspace.data.ptr, buffersize, 0, dev_info.data.ptr)

    status = int(dev_info[0])
    if status > 0:
        raise linalg.LinAlgError(
            'SVD computation does not converge')
    elif status < 0:
        raise linalg.LinAlgError(
            'Parameter error (maybe caused by a bug in cupy.linalg?)')

    # Note that the returned array may need to be transporsed
    # depending on the structure of an input
    if compute_uv:
        if trans_flag:
            return u.transpose(), s, vt.transpose()
        else:
            return vt, s, u
    else:
        return s