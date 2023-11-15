    def refresh(self, **kwargs):
        """
        Refreshes the plot by rerendering it and then pushing
        the updated data if the plot has an associated Comm.
        """
        if self.renderer.mode == 'server':
            from bokeh.io import curdoc
            thread = threading.current_thread()
            thread_id = thread.ident if thread else None
            if (curdoc() is not self.document or (state._thread_id is not None and
                thread_id != state._thread_id)):
                # If we do not have the Document lock, schedule refresh as callback
                self._triggering += [s for p in self.traverse(lambda x: x, [Plot])
                                     for s in getattr(p, 'streams', []) if s._triggering]
                if self.document.session_context:
                    self.document.add_next_tick_callback(self.refresh)
                    return

        # Ensure that server based tick callbacks maintain stream triggering state
        for s in self._triggering:
            s._triggering = True
        try:
            traverse_setter(self, '_force', True)
            key = self.current_key if self.current_key else self.keys[0]
            dim_streams = [stream for stream in self.streams
                           if any(c in self.dimensions for c in stream.contents)]
            stream_params = stream_parameters(dim_streams)
            key = tuple(None if d in stream_params else k
                        for d, k in zip(self.dimensions, key))
            stream_key = util.wrap_tuple_streams(key, self.dimensions, self.streams)

            self._trigger_refresh(stream_key)
            if self.top_level:
                self.push()
        except Exception as e:
            raise e
        finally:
            # Reset triggering state
            for s in self._triggering:
                s._triggering = False
            self._triggering = []