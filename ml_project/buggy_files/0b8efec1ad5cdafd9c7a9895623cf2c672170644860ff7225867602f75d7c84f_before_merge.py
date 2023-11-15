	def specific_warning(message, stacklevel=1, since=None, includedoc=None, extenddoc=False):
		def decorator(func):
			func.__qualname__ = to_native_str('warning_decorator_factory')
			func.__annotations__ = dict()
			@wraps(func)
			def func_wrapper(*args, **kwargs):
				# we need to increment the stacklevel by one because otherwise we'll get the location of our
				# func_wrapper in the log, instead of our caller (which is the real caller of the wrapped function)
				warnings.warn(message, warning_type, stacklevel=stacklevel + 1)
				return func(*args, **kwargs)

			if includedoc is not None and since is not None:
				docstring = "\n.. deprecated:: {since}\n   {message}\n\n".format(since=since, message=includedoc)
				if extenddoc and hasattr(func_wrapper, "__doc__") and func_wrapper.__doc__ is not None:
					docstring = func_wrapper.__doc__ + "\n" + docstring
				func_wrapper.__doc__ = docstring

			return func_wrapper

		return decorator