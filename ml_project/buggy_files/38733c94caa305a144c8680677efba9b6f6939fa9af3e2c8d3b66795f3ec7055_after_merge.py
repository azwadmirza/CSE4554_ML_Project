def script(vm_):
    """
    Return the script deployment object
    """
    return ScriptDeployment(
        salt.utils.cloud.os_script(
            salt.config.get_cloud_config_value("os", vm_, __opts__),
            vm_,
            __opts__,
            salt.utils.cloud.salt_config_to_yaml(
                salt.utils.cloud.minion_config(__opts__, vm_)
            ),
        )
    )