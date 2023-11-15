def cache(call: Callable):
  """Memoization decorator for functions taking a WrappedFun as first argument.

  Args:
    call: a Python callable that takes a WrappedFun as its first argument. The
      underlying transforms and params on the WrappedFun are used as part of the
      memoization cache key.

  Returns:
     A memoized version of ``call``.
  """
  fun_caches: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
  thread_local: threading.local = _CacheLocalContext()

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

  def _most_recent_entry():
    most_recent_entry = thread_local.most_recent_entry
    if most_recent_entry is not None:
      result = most_recent_entry()
      thread_local.most_recent_entry = None
      return result

  memoized_fun.most_recent_entry = _most_recent_entry  # type: ignore
  memoized_fun.cache_clear = fun_caches.clear  # type: ignore

  return memoized_fun