    def widgets_from_dimensions(cls, object, widget_types=None, widgets_type='individual'):
        from holoviews.core import Dimension, DynamicMap
        from holoviews.core.options import SkipRendering
        from holoviews.core.util import isnumeric, unicode, datetime_types, unique_iterator
        from holoviews.core.traversal import unique_dimkeys
        from holoviews.plotting.plot import Plot, GenericCompositePlot
        from holoviews.plotting.util import get_dynamic_mode
        from ..widgets import Widget, DiscreteSlider, Select, FloatSlider, DatetimeInput, IntSlider

        if widget_types is None:
            widget_types = {}

        if isinstance(object, GenericCompositePlot):
            object = object.layout
        elif isinstance(object, Plot):
            object = object.hmap

        if isinstance(object, DynamicMap) and object.unbounded:
            dims = ', '.join('%r' % dim for dim in object.unbounded)
            msg = ('DynamicMap cannot be displayed without explicit indexing '
                   'as {dims} dimension(s) are unbounded. '
                   '\nSet dimensions bounds with the DynamicMap redim.range '
                   'or redim.values methods.')
            raise SkipRendering(msg.format(dims=dims))

        dynamic, bounded = get_dynamic_mode(object)
        dims, keys = unique_dimkeys(object)
        if dims == [Dimension('Frame')] and keys == [(0,)]:
            return [], {}

        nframes = 1
        values = dict() if dynamic else dict(zip(dims, zip(*keys)))
        dim_values = OrderedDict()
        widgets = []
        dims = [d for d in dims if values.get(d) is not None or
                d.values or d.range != (None, None)]

        for i, dim in enumerate(dims):
            widget_type, widget, widget_kwargs = None, None, {}

            if widgets_type == 'individual':
                if i == 0 and i == (len(dims)-1):
                    margin = (20, 20, 20, 20)
                elif i == 0:
                    margin = (20, 20, 5, 20)
                elif i == (len(dims)-1):
                    margin = (5, 20, 20, 20)
                else:
                    margin = (0, 20, 5, 20)
                kwargs = {'margin': margin, 'width': 250}
            else:
                kwargs = {}

            vals = dim.values or values.get(dim, None)
            if vals is not None:
                vals = list(unique_iterator(vals))
            dim_values[dim.name] = vals
            if widgets_type == 'scrubber':
                if not vals:
                    raise ValueError('Scrubber widget may only be used if all dimensions define values.')
                nframes *= len(vals)
            elif dim.name in widget_types:
                widget = widget_types[dim.name]
                if isinstance(widget, Widget):
                    widget.set_param(**kwargs)
                    if not widget.name:
                        widget.name = dim.label
                    widgets.append(widget)
                    continue
                elif isinstance(widget, dict):
                    widget_type = widget.get('type', widget_type)
                    widget_kwargs = dict(widget)
                elif isinstance(widget, type) and issubclass(widget, Widget):
                    widget_type = widget
                else:
                    raise ValueError('Explicit widget definitions expected '
                                     'to be a widget instance or type, %s '
                                     'dimension widget declared as %s.' %
                                     (dim, widget))
            widget_kwargs.update(kwargs)

            if vals:
                if all(isnumeric(v) or isinstance(v, datetime_types) for v in vals) and len(vals) > 1:
                    vals = sorted(vals)
                    labels = [unicode(dim.pprint_value(v)) for v in vals]
                    options = OrderedDict(zip(labels, vals))
                    widget_type = widget_type or DiscreteSlider
                else:
                    options = list(vals)
                    widget_type = widget_type or Select
                default = vals[0] if dim.default is None else dim.default
                widget_kwargs = dict(dict(name=dim.label, options=options, value=default), **widget_kwargs)
                widget = widget_type(**widget_kwargs)
            elif dim.range != (None, None):
                start, end = dim.range
                if start == end:
                    continue
                default = start if dim.default is None else dim.default
                if widget_type is not None:
                    pass
                elif all(isinstance(v, int) for v in (start, end, default)):
                    widget_type = IntSlider
                    step = 1 if dim.step is None else dim.step
                elif isinstance(default, datetime_types):
                    widget_type = DatetimeInput
                else:
                    widget_type = FloatSlider
                    step = 0.1 if dim.step is None else dim.step
                widget_kwargs = dict(dict(step=step, name=dim.label, start=dim.range[0],
                                          end=dim.range[1], value=default),
                                     **widget_kwargs)
                widget = widget_type(**widget_kwargs)
            if widget is not None:
                widgets.append(widget)
        if widgets_type == 'scrubber':
            widgets = [Player(length=nframes, width=550)]
        return widgets, dim_values