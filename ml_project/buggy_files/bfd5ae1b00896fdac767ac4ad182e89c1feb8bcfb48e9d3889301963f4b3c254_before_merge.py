		def validator(phase, plugin_info):
			if phase == "after_load":
				setattr(plugin_info, "safe_mode_victim", not plugin_info.bundled)
				setattr(plugin_info, "safe_mode_enabled", False)
			elif phase == "before_enable":
				if not plugin_info.bundled:
					setattr(plugin_info, "safe_mode_enabled", True)
					return False
			return True