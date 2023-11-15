def build_tagger_model(nr_class, **cfg):
    embed_size = util.env_opt('embed_size', 7000)
    if 'token_vector_width' in cfg:
        token_vector_width = cfg['token_vector_width']
    else:
        token_vector_width = util.env_opt('token_vector_width', 128)
    pretrained_vectors = cfg.get('pretrained_vectors')
    with Model.define_operators({'>>': chain, '+': add}):
        if 'tok2vec' in cfg:
            tok2vec = cfg['tok2vec']
        else:
            tok2vec = Tok2Vec(token_vector_width, embed_size,
                              pretrained_vectors=pretrained_vectors)
        softmax = with_flatten(Softmax(nr_class, token_vector_width))
        model = (
            tok2vec
            >> softmax
        )
    model.nI = None
    model.tok2vec = tok2vec
    model.softmax = softmax
    return model