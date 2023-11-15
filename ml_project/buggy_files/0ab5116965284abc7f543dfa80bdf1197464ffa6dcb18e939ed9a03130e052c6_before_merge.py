def vmap(fun: Callable, in_axes=0, out_axes=0):
  """Vectorizing map. Creates a function which maps `fun` over argument axes.

  Args:
    fun: Function to be mapped over additional axes.
    in_axes: A nonnegative integer, None, or (nested) standard Python container
      (tuple/list/dict) thereof specifying which input array axes to map over.
      If each positional argument to ``fun`` is an array, then ``in_axes`` can
      be a nonnegative integer, a None, or a tuple of integers and Nones with
      length equal to the number of positional arguments to ``fun``. An integer
      or None indicates which array axis to map over for all arguments (with
      None indicating not to map any axis), and a tuple indicates which axis to
      map for each corresponding positional argument. If the positional
      arguments to ``fun`` are container types, the corresponding element of
      ``in_axes`` can itself be a matching container, so that distinct array
      axes can be mapped for different container elements. ``in_axes`` must be a
      container tree prefix of the positional argument tuple passed to ``fun``.
    out_axes: A nonnegative integer, None, or (nested) standard Python container
      (tuple/list/dict) thereof indicating where the mapped axis should appear
      in the output.

  Returns:
    Batched/vectorized version of ``fun`` with arguments that correspond to
    those of ``fun``, but with extra array axes at positions indicated by
    ``in_axes``, and a return value that corresponds to that of ``fun``, but
    with extra array axes at positions indicated by ``out_axes``.

  For example, we can implement a matrix-matrix product using a vector dot
  product:

  >>> vv = lambda x, y: np.vdot(x, y)  #  ([a], [a]) -> []
  >>> mv = vmap(vv, (0, None), 0)      #  ([b,a], [a]) -> [b]      (b is the mapped axis)
  >>> mm = vmap(mv, (None, 1), 1)      #  ([b,a], [a,c]) -> [b,c]  (c is the mapped axis)

  Here we use ``[a,b]`` to indicate an array with shape (a,b). Here are some
  variants:

  >>> mv1 = vmap(vv, (0, 0), 0)   #  ([b,a], [b,a]) -> [b]        (b is the mapped axis)
  >>> mv2 = vmap(vv, (0, 1), 0)   #  ([b,a], [a,b]) -> [b]        (b is the mapped axis)
  >>> mm2 = vmap(mv2, (1, 1), 0)  #  ([b,c,a], [a,c,b]) -> [c,b]  (c is the mapped axis)

  Here's an example of using container types in ``in_axes`` to specify which
  axes of the container elements to map over:

  >>> A, B, C, D = 2, 3, 4, 5
  >>> x = np.ones((A, B))
  >>> y = np.ones((B, C))
  >>> z = np.ones((C, D))
  >>> def foo(tree_arg):
  ...   x, (y, z) = tree_arg
  ...   return np.dot(x, np.dot(y, z))
  >>> tree = (x, (y, z))
  >>> print(foo(tree))
  [[12. 12. 12. 12. 12.]
   [12. 12. 12. 12. 12.]]
  >>> from jax import vmap
  >>> K = 6  # batch size
  >>> x = np.ones((K, A, B))  # batch axis in different locations
  >>> y = np.ones((B, K, C))
  >>> z = np.ones((C, D, K))
  >>> tree = (x, (y, z))
  >>> vfoo = vmap(foo, in_axes=((0, (1, 2)),))
  >>> print(vfoo(tree)).shape
  (6, 2, 5)
  """
  docstr = ("Vectorized version of {fun}. Takes similar arguments as {fun} "
            "but with additional array axes over which {fun} is mapped.")

  _check_callable(fun)
  if (not isinstance(in_axes, (list, tuple, type(None), int))
      or not isinstance(out_axes, (list, tuple, type(None), int))):
    msg = ("vmap arguments in_axes and out_axes must each be an integer, None, "
           "or a (nested) tuple of those types, got {} and {} respectively.")
    raise TypeError(msg.format(type(in_axes), type(out_axes)))

  def _check_axis_sizes(tree, vals, dims):
    mapped_axis_sizes = {x.shape[d] for x, d in zip(vals, dims) if d is not None}
    try:
      sizes, = mapped_axis_sizes
    except ValueError as e:
      msg = "vmap got inconsistent sizes for array axes to be mapped:\n{}"
      # we switch the error message based on whether args is a tuple of arrays,
      # in which case we can produce an error message based on argument indices,
      # or if it has nested containers.
      # TODO(mattjj,phawkins): add a way to inspect pytree kind more directly
      if tree == tree_flatten((core.unit,) * tree.num_leaves)[1]:
        lines1 = ["arg {} has shape {} and axis {} is to be mapped"
                  .format(i, x.shape, d) for i, (x, d) in enumerate(zip(vals, dims))]
        sizes = collections.defaultdict(list)
        for i, (x, d) in enumerate(zip(vals, dims)):
          if d is not None:
            sizes[x.shape[d]].append(i)
        lines2 = ["{} {} {} {} to be mapped of size {}".format(
                   "args" if len(idxs) > 1 else "arg",
                   ", ".join(map(str, idxs)),
                   "have" if len(idxs) > 1 else "has",
                   "axes" if len(idxs) > 1 else "an axis",
                   size)
                  for size, idxs in sizes.items()]
        raise ValueError(msg.format("\n".join(lines1 + ["so"] + lines2))) from e
      else:
        sizes = [x.shape[d] if d is not None else None for x, d in zip(vals, dims)]
        sizes = tree_unflatten(tree, sizes)
        raise ValueError(msg.format("the tree of axis sizes is:\n{}".format(sizes))) from e

  @wraps(fun, docstr=docstr)
  def batched_fun(*args):
    args_flat, in_tree  = tree_flatten(args)
    f = lu.wrap_init(fun)
    flat_fun, out_tree = flatten_fun_nokwargs(f, in_tree)
    in_axes_flat = _flatten_axes(in_tree, in_axes)
    _check_axis_sizes(in_tree, args_flat, in_axes_flat)
    out_flat = batching.batch(flat_fun, args_flat, in_axes_flat,
                              lambda: _flatten_axes(out_tree(), out_axes))
    return tree_unflatten(out_tree(), out_flat)

  return batched_fun