  def custom_jvp(primals, tangents):
    ans = fun(*primals)
    tangents_out = [rule(t, ans, *primals) for rule, t in zip(jvprules, tangents)
                    if rule is not None and t is not ad_util.zero]
    return ans, functools.reduce(ad.add_tangents, tangents_out, ad_util.zero)