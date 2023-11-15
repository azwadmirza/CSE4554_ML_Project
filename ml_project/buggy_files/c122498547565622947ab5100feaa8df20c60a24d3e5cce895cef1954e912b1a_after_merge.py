    def __init__(self, folder, data_callback, error_callback=None):
        self.files = find_files(folder)
        self.data_callback = data_callback
        self.error_callback = error_callback
        self.loop = gobject.MainLoop()

        fakesink = gst.element_factory_make('fakesink')

        self.uribin = gst.element_factory_make('uridecodebin')
        self.uribin.set_property('caps', gst.Caps('audio/x-raw-int'))
        self.uribin.connect('pad-added', self.process_new_pad,
            fakesink.get_pad('sink'))

        self.pipe = gst.element_factory_make('pipeline')
        self.pipe.add(self.uribin)
        self.pipe.add(fakesink)

        bus = self.pipe.get_bus()
        bus.add_signal_watch()
        bus.connect('message::tag', self.process_tags)
        bus.connect('message::error', self.process_error)