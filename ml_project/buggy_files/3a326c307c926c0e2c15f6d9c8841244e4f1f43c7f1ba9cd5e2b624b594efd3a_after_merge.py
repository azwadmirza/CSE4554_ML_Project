def my_odeint_jacrev(fun):
  """Calculate the Jacobian of an odeint."""
  @jax.jit
  def _jacfun(*args, **kwargs):
    ys, pullback = vjp_odeint(fun, *args, **kwargs)
    my_jac = jax.vmap(pullback)(jax.api._std_basis(ys))
    my_jac = jax.api.tree_map(
        partial(jax.api._unravel_array_into_pytree, ys, 0), my_jac)
    my_jac = jax.api.tree_transpose(
        jax.api.tree_structure(args), jax.api.tree_structure(ys), my_jac)
    return my_jac
  return _jacfun