def add_decorate(orig, fill_value=None, **decorate):
    """Decorate an image with text and/or logos/images.

    This call adds text/logos in order as given in the input to keep the
    alignment features available in pydecorate.

    An example of the decorate config::

        decorate = {
            'decorate': [
                {'logo': {'logo_path': <path to a logo>, 'height': 143, 'bg': 'white', 'bg_opacity': 255}},
                {'text': {'txt': start_time_txt,
                          'align': {'top_bottom': 'bottom', 'left_right': 'right'},
                          'font': <path to ttf font>,
                          'font_size': 22,
                          'height': 30,
                          'bg': 'black',
                          'bg_opacity': 255,
                          'line': 'white'}}
            ]
        }

    Any numbers of text/logo in any order can be added to the decorate list,
    but the order of the list is kept as described above.

    Note that a feature given in one element, eg. bg (which is the background color)
    will also apply on the next elements  unless a new value is given.

    align is a special keyword telling where in the image to start adding features, top_bottom is either top or bottom
    and left_right is either left or right.
    """
    LOG.info("Decorate image.")

    # Need to create this here to possible keep the alignment
    # when adding text and/or logo with pydecorate
    if hasattr(orig, 'convert'):
        # image must be in RGB space to work with pycoast/pydecorate
        orig = orig.convert('RGBA' if orig.mode.endswith('A') else 'RGB')
    elif not orig.mode.startswith('RGB'):
        raise RuntimeError("'trollimage' 1.6+ required to support adding "
                           "overlays/decorations to non-RGB data.")
    img_orig = orig.pil_image(fill_value=fill_value)
    from pydecorate import DecoratorAGG
    dc = DecoratorAGG(img_orig)

    # decorate need to be a list to maintain the alignment
    # as ordered in the list
    img = orig
    if 'decorate' in decorate:
        for dec in decorate['decorate']:
            if 'logo' in dec:
                img = add_logo(img, dc, img_orig, logo=dec['logo'])
            elif 'text' in dec:
                img = add_text(img, dc, img_orig, text=dec['text'])
    return img