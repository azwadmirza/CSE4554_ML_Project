		def validator(phase, plugin_info):
			if phase in ("before_import", "before_load", "before_enable"):
				setattr(plugin_info, "safe_mode_victim", not plugin_info.bundled)
				if not plugin_info.bundled:
					return False
			return True