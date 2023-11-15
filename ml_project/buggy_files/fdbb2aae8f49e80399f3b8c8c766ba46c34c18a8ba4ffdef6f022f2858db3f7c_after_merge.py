    def on_prop_changed(adapter, key, value, _path):
        if key == "Powered" and value:
            GLib.source_remove(source)
            adapter.disconnect_signal(sig)
            callback()