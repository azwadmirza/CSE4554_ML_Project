    def validate_coerce(self, v, skip_invalid=False):

        # Import Histogram2dcontour, this is the deprecated name of the
        # Histogram2dContour trace.
        from plotly.graph_objs import Histogram2dcontour

        if v is None:
            v = []
        elif isinstance(v, (list, tuple)):
            trace_classes = tuple(self.class_map.values())

            res = []
            invalid_els = []
            for v_el in v:

                if isinstance(v_el, trace_classes):
                    # Clone input traces
                    v_el = v_el.to_plotly_json()

                if isinstance(v_el, dict):
                    v_copy = deepcopy(v_el)

                    if 'type' in v_copy:
                        trace_type = v_copy.pop('type')
                    elif isinstance(v_el, Histogram2dcontour):
                        trace_type = 'histogram2dcontour'
                    else:
                        trace_type = 'scatter'

                    if trace_type not in self.class_map:
                        if skip_invalid:
                            # Treat as scatter trace
                            trace = self.class_map['scatter'](
                                skip_invalid=skip_invalid, **v_copy)
                            res.append(trace)
                        else:
                            res.append(None)
                            invalid_els.append(v_el)
                    else:
                        trace = self.class_map[trace_type](
                            skip_invalid=skip_invalid, **v_copy)
                        res.append(trace)
                else:
                    if skip_invalid:
                        # Add empty scatter trace
                        trace = self.class_map['scatter']()
                        res.append(trace)
                    else:
                        res.append(None)
                        invalid_els.append(v_el)

            if invalid_els:
                self.raise_invalid_elements(invalid_els)

            v = to_scalar_or_list(res)

            # Set new UIDs
            if self.set_uid:
                for trace in v:
                    trace.uid = str(uuid.uuid1())

        else:
            if skip_invalid:
                v = []
            else:
                self.raise_invalid_val(v)

        return v