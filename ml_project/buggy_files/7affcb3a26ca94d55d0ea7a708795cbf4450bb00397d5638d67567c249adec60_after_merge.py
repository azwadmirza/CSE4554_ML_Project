def jaxpr_replicas(jaxpr):
  return max(it.chain([1], (eqn_replicas(eqn) for eqn in jaxpr.eqns)))