def render(request, project, widget='287x66', color=None, lang=None):
    obj = get_object_or_404(Project, slug=project)

    # Handle language parameter
    if lang is not None:
        try:
            django.utils.translation.activate(lang)
        except:
            # Ignore failure on activating language
            pass
        try:
            lang = Language.objects.get(code=lang)
        except Language.DoesNotExist:
            lang = None

    percent = obj.get_translated_percent(lang)

    # Get widget data
    try:
        widget_data = WIDGETS[widget]
    except KeyError:
        raise Http404()

    # Get widget color
    if color not in widget_data['colors']:
        color = widget_data['default']

    # Background 287 x 66, logo 64 px
    surface = cairo.ImageSurface.create_from_png(
        os.path.join(appsettings.WEB_ROOT, 'media', widget_data['name'] % {
            'color': color,
            'widget': widget,
        })
    )
    ctx = cairo.Context(surface)

    # Setup
    ctx.set_line_width(widget_data['colors'][color]['line'])

    # Progress bar rendering
    if widget_data['progress'] is not None:
        # Filled bar
        ctx.new_path()
        ctx.set_source_rgb (*widget_data['colors'][color]['bar'])
        if widget_data['progress']['horizontal']:
            ctx.rectangle(
                widget_data['progress']['x'],
                widget_data['progress']['y'],
                widget_data['progress']['width'] / 100.0 * percent,
                widget_data['progress']['height']
            )
        else:
            diff = widget_data['progress']['height'] / 100.0 * (100 - percent)
            ctx.rectangle(
                widget_data['progress']['x'],
                widget_data['progress']['y'] + diff,
                widget_data['progress']['width'],
                widget_data['progress']['height'] - diff
            )
        ctx.fill()

        # Progress border
        ctx.new_path()
        ctx.set_source_rgb (*widget_data['colors'][color]['border'])
        ctx.rectangle(
            widget_data['progress']['x'],
            widget_data['progress']['y'],
            widget_data['progress']['width'],
            widget_data['progress']['height']
        )
        ctx.stroke()

    # Text rendering
    # Set text color
    ctx.set_source_rgb (*widget_data['colors'][color]['text'])

    # Create pango context
    pangocairo_context = pangocairo.CairoContext(ctx)
    pangocairo_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

    # Text format strings
    params =  {
        'name': obj.name,
        'count': obj.get_total(),
        'languages': obj.get_language_count(),
        'percent': percent,
    }

    for line in widget_data['text']:
        # Format text
        text = line['text']
        if lang is not None and 'text_lang' in line:
            text = line['text_lang']
            if 'English' in text:
                text = text.replace('English', lang.name)
        text = text % params

        font_size = line['font_size']

        # Render text
        layout = render_text(pangocairo_context, line, text, params, font_size)

        # Fit text to image if it is too big
        extent = layout.get_pixel_extents()
        width = surface.get_width()
        while extent[1][2] + line['pos'][0] > width and font_size > 4:
            font_size -= 1
            layout = render_text(
                pangocairo_context,
                line,
                text,
                params,
                font_size
            )
            extent = layout.get_pixel_extents()

        # Set position
        ctx.move_to(*line['pos'])

        # Render to cairo context
        pangocairo_context.update_layout(layout)
        pangocairo_context.show_layout(layout)

    # Render PNG
    out = StringIO()
    surface.write_to_png(out)
    data = out.getvalue()

    return HttpResponse(content_type='image/png', content=data)