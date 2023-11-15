			def key_func(x):
				config = templates[t]["entries"][x]
				entry_order = config_extractor(config, "order", default_value=None)
				return entry_order is None, sv(entry_order)