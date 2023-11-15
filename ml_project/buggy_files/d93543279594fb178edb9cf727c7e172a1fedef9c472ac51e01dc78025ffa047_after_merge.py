def cholesky(a, lower=False, overwrite_a=False, check_finite=True):
  warnings.warn(_EXPERIMENTAL_WARNING)
  del overwrite_a, check_finite
  a = np_linalg._promote_arg_dtypes(np.asarray(a))
  l = lax_linalg.cholesky(a if lower else np.conj(_T(a)), symmetrize_input=False)
  return l if lower else np.conj(_T(l))