def scrape_prometheus(endpoints, retries=3, err_output_file=sys.stdout):
    """Scrape a list of Prometheus/FAUCET/Gauge endpoints and aggregate results."""
    metrics = []
    for endpoint in endpoints:
        content = None
        err = None
        for _ in range(retries):
            try:
                if endpoint.startswith('http'):
                    response = requests.get(endpoint)
                    if response.status_code == requests.status_codes.codes.ok: # pylint: disable=no-member
                        content = response.content.decode('utf-8', 'strict')
                        break
                else:
                    response = urllib.request.urlopen(endpoint) # pytype: disable=module-attr
                    content = response.read().decode('utf-8', 'strict')
                    break
            except (requests.exceptions.ConnectionError, ValueError) as exception:
                err = exception
                time.sleep(1)
        if err is not None:
            err_output_file.write(str(err))
            return None
        try:
            endpoint_metrics = parser.text_string_to_metric_families(
                content)
            metrics.extend(endpoint_metrics)
        except ValueError as err:
            err_output_file.write(str(err))
            return None
    return metrics