    def perform_statistics(self, server, pingback_id):

        url = urljoin(server, "/api/v1/statistics")

        channels = [extract_channel_statistics(c) for c in ChannelMetadata.objects.all()]
        facilities = [extract_facility_statistics(f) for f in Facility.objects.all()]

        data = {
            "pi": pingback_id,
            "c": channels,
            "f": facilities,
        }

        logger.debug("Statistics data: {}".format(data))

        jsondata = dump_zipped_json(data)

        response = requests.post(url, data=jsondata, timeout=60)

        response.raise_for_status()

        return json.loads(response.content or "{}")