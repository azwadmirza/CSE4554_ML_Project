    def perform_ping(self, server):

        url = urljoin(server, "/api/v1/pingback")

        instance, _ = InstanceIDModel.get_or_create_current_instance()

        devicesettings = DeviceSettings.objects.first()
        language = devicesettings.language_id if devicesettings else ""

        try:
            timezone = get_current_timezone().zone
        except Exception:
            timezone = ""

        data = {
            "instance_id": instance.id,
            "version": kolibri.__version__,
            "mode": os.environ.get("KOLIBRI_RUN_MODE", ""),
            "platform": instance.platform,
            "sysversion": instance.sysversion,
            "database_id": instance.database.id,
            "system_id": instance.system_id,
            "node_id": instance.node_id,
            "language": language,
            "timezone": timezone,
            "uptime": int((datetime.now() - self.started).total_seconds() / 60),
        }

        logger.debug("Pingback data: {}".format(data))

        jsondata = dump_zipped_json(data)

        response = requests.post(url, data=jsondata, timeout=60)

        response.raise_for_status()

        return json.loads(response.content or "{}")