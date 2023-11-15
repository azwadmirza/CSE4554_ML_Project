def eqn_replicas(eqn):
  (subjaxpr, _, _), = eqn.bound_subjaxprs
  return eqn.params.get('axis_size', 1) * jaxpr_replicas(subjaxpr)