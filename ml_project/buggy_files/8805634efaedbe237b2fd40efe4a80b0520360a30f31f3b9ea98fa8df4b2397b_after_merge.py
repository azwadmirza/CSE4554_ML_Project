def read_last_influxdb(device_id, measure_type, duration_sec=None):
    """
    Query Influxdb for the last entry.

    example:
        read_last_influxdb('00000001', 'temperature')

    :return: list of time and value
    :rtype: list

    :param device_id: What device_id tag to query in the Influxdb
        database (ex. '00000001')
    :type device_id: str
    :param measure_type: What measurement to query in the Influxdb
        database (ex. 'temperature', 'duration')
    :type measure_type: str
    :param duration_sec: How many seconds to look for a past measurement
    :type duration_sec: int
    """
    client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_USER,
                            INFLUXDB_PASSWORD, INFLUXDB_DATABASE)

    if duration_sec:
        query = query_string(measure_type, device_id, past_sec=duration_sec)
    else:
        query = query_string(measure_type, device_id, value='LAST')

    try:
        last_measurement = client.query(query).raw
    except requests.exceptions.ConnectionError:
        logger.debug("Failed to establish a new influxdb connection. Ensure influxdb is running.")
        last_measurement = None

    if last_measurement:
        try:
            number = len(last_measurement['series'][0]['values'])
            last_time = last_measurement['series'][0]['values'][number - 1][0]
            last_measurement = last_measurement['series'][0]['values'][number - 1][1]
            return [last_time, last_measurement]
        except KeyError:
            if duration_sec:
                logger.debug("No measurement available in the past "
                             "{sec} seconds.".format(sec=duration_sec))
            else:
                logger.debug("No measurement available.")
        except Exception:
            logger.exception("Error parsing the last influx measurement")