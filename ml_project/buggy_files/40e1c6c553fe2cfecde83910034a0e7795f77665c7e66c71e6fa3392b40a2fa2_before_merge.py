def compiled_call_impl(fun, *args):
  with new_master(JaxprTrace, True) as master:
    pvals = map(abstractify, args)
    jaxpr, (pval, consts, env) = trace_to_subjaxpr(fun, master).call_wrapped(pvals)
    jaxpr_ans = eval_jaxpr_raw(jaxpr, consts, env, *args)
    ans = merge_pvals(jaxpr_ans, pval)
    del master, pvals, pval, consts, env, jaxpr_ans, jaxpr
    return ans