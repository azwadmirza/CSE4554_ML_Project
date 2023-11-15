    def napalm(self, request, pk):
        """
        Execute a NAPALM method on a Device
        """
        device = get_object_or_404(Device, pk=pk)
        if not device.primary_ip:
            raise ServiceUnavailable("This device does not have a primary IP address configured.")
        if device.platform is None:
            raise ServiceUnavailable("No platform is configured for this device.")
        if not device.platform.napalm_driver:
            raise ServiceUnavailable("No NAPALM driver is configured for this device's platform ().".format(
                device.platform
            ))

        # Check that NAPALM is installed and verify the configured driver
        try:
            import napalm
            from napalm_base.exceptions import ConnectAuthError, ModuleImportError
        except ImportError:
            raise ServiceUnavailable("NAPALM is not installed. Please see the documentation for instructions.")
        try:
            driver = napalm.get_network_driver(device.platform.napalm_driver)
        except ModuleImportError:
            raise ServiceUnavailable("NAPALM driver for platform {} not found: {}.".format(
                device.platform, device.platform.napalm_driver
            ))

        # Verify user permission
        if not request.user.has_perm('dcim.napalm_read'):
            return HttpResponseForbidden()

        # Validate requested NAPALM methods
        napalm_methods = request.GET.getlist('method')
        for method in napalm_methods:
            if not hasattr(driver, method):
                return HttpResponseBadRequest("Unknown NAPALM method: {}".format(method))
            elif not method.startswith('get_'):
                return HttpResponseBadRequest("Unsupported NAPALM method: {}".format(method))

        # Connect to the device and execute the requested methods
        # TODO: Improve error handling
        response = OrderedDict([(m, None) for m in napalm_methods])
        ip_address = str(device.primary_ip.address.ip)
        d = driver(
            hostname=ip_address,
            username=settings.NAPALM_USERNAME,
            password=settings.NAPALM_PASSWORD,
            timeout=settings.NAPALM_TIMEOUT,
            optional_args=settings.NAPALM_ARGS
        )
        try:
            d.open()
            for method in napalm_methods:
                response[method] = getattr(d, method)()
        except Exception as e:
            raise ServiceUnavailable("Error connecting to the device at {}: {}".format(ip_address, e))

        d.close()
        return Response(response)