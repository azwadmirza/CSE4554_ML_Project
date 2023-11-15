def arange(*args, **kwargs):
  dtype = kwargs.get("dtype", None)
  if not args:
    raise TypeError("Required argument 'start' (pos 1) not found")  # same as numpy error

  # If called like np.arange(N), we create a lazy lax._IotaConstant.
  if len(args) == 1 and not kwargs:
    stop, = args
    dtype = dtype or _dtype(stop)
    if onp.issubdtype(dtype, onp.integer):
      return lax.iota(dtype, stop)  # avoids materializing

  # Fall back to instantiating an ndarray in host memory
  return onp.arange(*args, **kwargs)