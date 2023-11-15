    def get_entry_points():
        yield from pkg_resources.iter_entry_points("hypothesis")