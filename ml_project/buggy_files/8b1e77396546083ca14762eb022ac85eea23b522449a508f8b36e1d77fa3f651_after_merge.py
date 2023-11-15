  def memoized_fun(fun: WrappedFun, *args):
    cache = fun_caches.setdefault(fun.f, {})
    if core.debug_state.check_leaks:
      key = (_copy_main_traces(fun.transforms), fun.params, args, config.x64_enabled)
    else:
      key = (fun.transforms, fun.params, args, config.x64_enabled)
    result = cache.get(key, None)
    if result is not None:
      ans, stores = result
      fun.populate_stores(stores)
    else:
      ans = call(fun, *args)
      cache[key] = (ans, fun.stores)

    thread_local.most_recent_entry = weakref.ref(ans)
    return ans