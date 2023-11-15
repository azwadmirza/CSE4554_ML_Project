def get_export_names(config=get_config()):
    """Return a list of the currently supported export targets

    Exporters can be found in external packages by registering
    them as an nbconvert.exporter entrypoint.
    """
    exporters = sorted(entrypoints.get_group_named('nbconvert.exporters'))
    enabled_exporters = []
    for exporter_name in exporters:
        try:
            e = get_exporter(exporter_name)(config=config)
            if e.enabled:
                enabled_exporters.append(exporter_name)
        except ExporterDisabledError:
            pass
    return enabled_exporters