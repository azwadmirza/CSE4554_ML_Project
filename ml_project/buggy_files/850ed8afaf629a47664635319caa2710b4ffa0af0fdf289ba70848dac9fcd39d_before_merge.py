def make_thumbnail(in_fname, out_fname, width, height):
    """Make a thumbnail with the same aspect ratio centered in an
       image with a given width and height
    """
    img = Image.open(in_fname)
    width_in, height_in = img.size
    scale_w = width / float(width_in)
    scale_h = height / float(height_in)

    if height_in * scale_w <= height:
        scale = scale_w
    else:
        scale = scale_h

    width_sc = int(round(scale * width_in))
    height_sc = int(round(scale * height_in))

    # resize the image
    img.thumbnail((width_sc, height_sc), Image.ANTIALIAS)

    # insert centered
    thumb = Image.new('RGB', (width, height), (255, 255, 255))
    pos_insert = ((width - width_sc) // 2, (height - height_sc) // 2)
    thumb.paste(img, pos_insert)

    thumb.save(out_fname)
    # Use optipng to perform lossless compression on the resized image if
    # software is installed
    if os.environ.get('SKLEARN_DOC_OPTIPNG', False):
        try:
            subprocess.call(["optipng", "-quiet", "-o", "9", out_fname])
        except Exception:
            warnings.warn('Install optipng to reduce the size of the generated images')