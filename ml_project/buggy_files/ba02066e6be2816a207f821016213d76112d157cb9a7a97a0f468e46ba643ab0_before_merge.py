def build_embeddings(opt, word_field, feat_fields, for_encoder=True):
    """
    Args:
        opt: the option in current environment.
        word_dict(Vocab): words dictionary.
        feature_dicts([Vocab], optional): a list of feature dictionary.
        for_encoder(bool): build Embeddings for encoder or decoder?
    """
    emb_dim = opt.src_word_vec_size if for_encoder else opt.tgt_word_vec_size

    word_padding_idx = word_field.vocab.stoi[word_field.pad_token]
    num_word_embeddings = len(word_field.vocab)

    feat_pad_indices = [ff.vocab.stoi[ff.pad_token] for ff in feat_fields]
    num_feat_embeddings = [len(ff.vocab) for ff in feat_fields]

    emb = Embeddings(
        word_vec_size=emb_dim,
        position_encoding=opt.position_encoding,
        feat_merge=opt.feat_merge,
        feat_vec_exponent=opt.feat_vec_exponent,
        feat_vec_size=opt.feat_vec_size,
        dropout=opt.dropout,
        word_padding_idx=word_padding_idx,
        feat_padding_idx=feat_pad_indices,
        word_vocab_size=num_word_embeddings,
        feat_vocab_sizes=num_feat_embeddings,
        sparse=opt.optim == "sparseadam"
    )
    return emb