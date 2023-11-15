def get_sampling(im):
    # There's no subsampling when image have only 1 layer
    # (grayscale images) or when they are CMYK (4 layers),
    # so set subsampling to default value.
    #
    # NOTE: currently Pillow can't encode JPEG to YCCK format.
    # If YCCK support is added in the future, subsampling code will have
    # to be updated (here and in JpegEncode.c) to deal with 4 layers.
    if not hasattr(im, 'layers') or im.layers in (1, 4):
        return -1
    sampling = im.layer[0][1:3] + im.layer[1][1:3] + im.layer[2][1:3]
    return samplings.get(sampling, -1)