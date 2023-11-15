def jaxpr_replicas(jaxpr):
  nums = (eqn_replicas(eqn) for eqn in jaxpr.eqns if eqn.bound_subjaxprs)
  return max(it.chain([1], nums))  # max(itr, default=1)