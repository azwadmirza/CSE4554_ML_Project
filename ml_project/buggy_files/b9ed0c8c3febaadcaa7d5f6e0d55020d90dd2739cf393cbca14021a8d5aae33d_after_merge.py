    def _settingIsOverwritingInheritance(self, key: str, stack: ContainerStack = None) -> bool:
        has_setting_function = False
        if not stack:
            stack = self._active_container_stack
        if not stack: #No active container stack yet!
            return False
        containers = []

        ## Check if the setting has a user state. If not, it is never overwritten.
        has_user_state = stack.getProperty(key, "state") == InstanceState.User
        if not has_user_state:
            return False

        ## If a setting is not enabled, don't label it as overwritten (It's never visible anyway).
        if not stack.getProperty(key, "enabled"):
            return False

        ## Also check if the top container is not a setting function (this happens if the inheritance is restored).
        if isinstance(stack.getTop().getProperty(key, "value"), SettingFunction):
            return False

        ##  Mash all containers for all the stacks together.
        while stack:
            containers.extend(stack.getContainers())
            stack = stack.getNextStack()
        has_non_function_value = False
        for container in containers:
            try:
                value = container.getProperty(key, "value")
            except AttributeError:
                continue
            if value is not None:
                # If a setting doesn't use any keys, it won't change it's value, so treat it as if it's a fixed value
                has_setting_function = isinstance(value, SettingFunction)
                if has_setting_function:
                    for setting_key in value.getUsedSettingKeys():
                        if setting_key in self._active_container_stack.getAllKeys():
                            break # We found an actual setting. So has_setting_function can remain true
                    else:
                        # All of the setting_keys turned out to not be setting keys at all!
                        # This can happen due enum keys also being marked as settings.
                        has_setting_function = False

                if has_setting_function is False:
                    has_non_function_value = True
                    continue

            if has_setting_function:
                break  # There is a setting function somewhere, stop looking deeper.
        return has_setting_function and has_non_function_value