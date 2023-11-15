def url_to_destination(url, service_type="external"):
    parts = compat.urlparse.urlsplit(url)
    hostname = parts.hostname
    # preserve brackets for IPv6 URLs
    if "://[" in url:
        hostname = "[%s]" % hostname
    port = parts.port
    default_port = default_ports.get(parts.scheme, None)
    name = "%s://%s" % (parts.scheme, hostname)
    resource = hostname
    if not port and parts.scheme in default_ports:
        port = default_ports[parts.scheme]
    if port:
        if port != default_port:
            name += ":%d" % port
        resource += ":%d" % port
    return {"service": {"name": name, "resource": resource, "type": service_type}}