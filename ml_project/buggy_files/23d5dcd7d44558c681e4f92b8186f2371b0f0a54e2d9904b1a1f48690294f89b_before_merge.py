def _pseudo_inverse_sparse(L, rhoss, w=None, **pseudo_args):
    """
    Internal function for computing the pseudo inverse of an Liouvillian using
    sparse matrix methods. See pseudo_inverse for details.
    """

    N = np.prod(L.dims[0][0])

    rhoss_vec = operator_to_vector(rhoss)

    tr_op = tensor([identity(n) for n in L.dims[0][0]])
    tr_op_vec = operator_to_vector(tr_op)

    P = zcsr_kron(rhoss_vec.data, tr_op_vec.data.T)
    I = sp.eye(N*N, N*N, format='csr')
    Q = I - P
    
  
    if w is None:
        L =  1.0j*(1e-15)*spre(tr_op) + L
    else:
        if w != 0.0:
            L = 1.0j*w*spre(tr_op) + L
        else:
            L =  1.0j*(1e-15)*spre(tr_op) + L
        
        
    if pseudo_args['use_rcm']:
        perm = reverse_cuthill_mckee(L.data)
        A = sp_permute(L.data, perm, perm)
        Q = sp_permute(Q, perm, perm)
    else:
        if ss_args['solver'] == 'scipy':
            A = L.data.tocsc()
            A.sort_indices()
        
        
    
    if pseudo_args['method'] == 'splu':
        if settings.has_mkl:
            A = L.data.tocsr()
            A.sort_indices()
            LIQ = mkl_spsolve(A,Q.toarray())
        else:
       
            lu = sp.linalg.splu(A, permc_spec=pseudo_args['permc_spec'],
                            diag_pivot_thresh=pseudo_args['diag_pivot_thresh'],
                            options=dict(ILU_MILU=pseudo_args['ILU_MILU']))
            LIQ = lu.solve(Q.toarray())
         
            
    elif pseudo_args['method'] == 'spilu':
        
        lu = sp.linalg.spilu(A, permc_spec=pseudo_args['permc_spec'],
                             fill_factor=pseudo_args['fill_factor'], 
                             drop_tol=pseudo_args['drop_tol'])
        LIQ = lu.solve(Q.toarray())


    else:
        raise ValueError("unsupported method '%s'" % method)

    R = sp.csr_matrix(Q * LIQ)

    if pseudo_args['use_rcm']:
        rev_perm = np.argsort(perm)
        R = sp_permute(R, rev_perm, rev_perm, 'csr')

    return Qobj(R, dims=L.dims)