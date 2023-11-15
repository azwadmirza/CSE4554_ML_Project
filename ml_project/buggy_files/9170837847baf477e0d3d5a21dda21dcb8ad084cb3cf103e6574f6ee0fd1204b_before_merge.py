	def validate(self, phase, additional_validators=None):
		result = True

		if phase == "before_load":
			# if the plugin still uses __plugin_init__, log a deprecation warning and move it to __plugin_load__
			if hasattr(self.instance, self.__class__.attr_init):
				if not hasattr(self.instance, self.__class__.attr_load):
					# deprecation warning
					import warnings
					warnings.warn("{name} uses deprecated control property __plugin_init__, use __plugin_load__ instead".format(name=self.key), DeprecationWarning)

					# move it
					init = getattr(self.instance, self.__class__.attr_init)
					setattr(self.instance, self.__class__.attr_load, init)

				# delete __plugin_init__
				delattr(self.instance, self.__class__.attr_init)

		elif phase == "after_load":
			# if the plugin still uses __plugin_implementations__, log a deprecation warning and put the first
			# item into __plugin_implementation__
			if hasattr(self.instance, self.__class__.attr_implementations):
				if not hasattr(self.instance, self.__class__.attr_implementation):
					# deprecation warning
					import warnings
					warnings.warn("{name} uses deprecated control property __plugin_implementations__, use __plugin_implementation__ instead - only the first implementation of {name} will be recognized".format(name=self.key), DeprecationWarning)

					# put first item into __plugin_implementation__
					implementations = getattr(self.instance, self.__class__.attr_implementations)
					if len(implementations) > 0:
						setattr(self.instance, self.__class__.attr_implementation, implementations[0])

				# delete __plugin_implementations__
				delattr(self.instance, self.__class__.attr_implementations)

		if additional_validators is not None:
			for validator in additional_validators:
				result = result and validator(phase, self)

		return result