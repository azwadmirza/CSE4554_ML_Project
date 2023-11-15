            def _maybe_add_color(kwargs, style, i):
                if (not has_colors and
                    (style is None or re.match('[a-z]+', style) is None)
                    and 'color' not in kwargs):
                    kwargs['color'] = colors[i % len(colors)]