		def sort_func(impl):
			sorting_value = None
			if sorting_context is not None and isinstance(impl[1], SortablePlugin):
				try:
					sorting_value = impl[1].get_sorting_key(sorting_context)
				except Exception:
					self.logger.exception("Error while trying to retrieve sorting order for plugin {}".format(impl[0]))

				if sorting_value is not None:
					try:
						sorting_value = int(sorting_value)
					except ValueError:
						self.logger.warning("The order value returned by {} for sorting context {} is not a valid integer, ignoring it".format(impl[0], sorting_context))
						sorting_value = None

			plugin_info = self.get_plugin_info(impl[0], require_enabled=False)
			return sorting_value is None, sv(sorting_value), not plugin_info.bundled if plugin_info else True, sv(impl[0])