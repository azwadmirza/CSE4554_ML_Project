            def _maybe_add_color(kwargs, style, i):
                if (not has_colors and
                    (style is None or re.match('[a-z]+', style) is None)):
                    kwargs['color'] = colors[i % len(colors)]