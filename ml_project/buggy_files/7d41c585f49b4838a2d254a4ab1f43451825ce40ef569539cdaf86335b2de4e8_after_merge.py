def wait_for_adapter(bluez_adapter, callback, timeout=1000):
    def on_prop_changed(adapter, key, value, _path):
        if key == "Powered" and value:
            GLib.source_remove(source)
            adapter.disconnect_signal(sig)
            callback()

    def on_timeout():
        bluez_adapter.disconnect_signal(sig)
        GLib.source_remove(source)
        dprint(YELLOW("Warning:"),
               "Bluez didn't provide 'Powered' property in a reasonable timeout\nAssuming adapter is ready")
        callback()

    props = bluez_adapter.get_properties()
    if props["Address"] != "00:00:00:00:00:00":
        callback()
        return

    source = GLib.timeout_add(timeout, on_timeout)
    sig = bluez_adapter.connect_signal('property-changed', on_prop_changed)