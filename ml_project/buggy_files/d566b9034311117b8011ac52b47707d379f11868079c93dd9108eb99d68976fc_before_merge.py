def Tok2Vec(width, embed_size, **kwargs):
    pretrained_dims = kwargs.get('pretrained_dims', 0)
    cnn_maxout_pieces = kwargs.get('cnn_maxout_pieces', 2)
    cols = [ID, NORM, PREFIX, SUFFIX, SHAPE, ORTH]
    with Model.define_operators({'>>': chain, '|': concatenate, '**': clone,
                                 '+': add, '*': reapply}):
        norm = HashEmbed(width, embed_size, column=cols.index(NORM),
                         name='embed_norm')
        prefix = HashEmbed(width, embed_size//2, column=cols.index(PREFIX),
                           name='embed_prefix')
        suffix = HashEmbed(width, embed_size//2, column=cols.index(SUFFIX),
                           name='embed_suffix')
        shape = HashEmbed(width, embed_size//2, column=cols.index(SHAPE),
                          name='embed_shape')
        if pretrained_dims is not None and pretrained_dims >= 1:
            glove = StaticVectors(VECTORS_KEY, width, column=cols.index(ID))

            embed = uniqued(
                (glove | norm | prefix | suffix | shape)
                >> LN(Maxout(width, width*5, pieces=3)), column=5)
        else:
            embed = uniqued(
                (norm | prefix | suffix | shape)
                >> LN(Maxout(width, width*4, pieces=3)), column=5)

        convolution = Residual(
            ExtractWindow(nW=1)
            >> LN(Maxout(width, width*3, pieces=cnn_maxout_pieces))
        )

        tok2vec = (
            FeatureExtracter(cols)
            >> with_flatten(
                embed
                >> convolution ** 4, pad=4
            )
        )
        # Work around thinc API limitations :(. TODO: Revise in Thinc 7
        tok2vec.nO = width
        tok2vec.embed = embed
    return tok2vec