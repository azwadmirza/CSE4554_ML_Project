def load_embedding_from_path(args):
    """Load a TokenEmbedding."""
    if args.embedding_path.endswith('.bin'):
        with utils.print_time('load fastText model.'):
            model = \
                nlp.model.train.FasttextEmbeddingModel.load_fasttext_format(
                    args.embedding_path)
        idx_to_token = sorted(model._token_to_idx, key=model._token_to_idx.get)

        # Analogy task is open-vocabulary, so must keep all known words.
        # But if not evaluating analogy, no need to precompute now as all
        # words for closed vocabulary task can be obtained via the unknown
        # lookup
        if not args.analogy_datasets:
            # TODO(leezu): use shape (0, model.weight.shape[1]) once np shape
            # is supported by TokenEmbedding
            idx_to_token = ['<unk>']
            idx_to_vec = mx.nd.zeros((1,  model.weight.shape[1]))
        else:
            if args.analogy_max_vocab_size:
                idx_to_token = idx_to_token[:args.analogy_max_vocab_size]
            with utils.print_time('compute vectors for {} known '
                                  'words.'.format(len(idx_to_token))):
                idx_to_vec = model[idx_to_token]

        embedding = nlp.embedding.TokenEmbedding(
            unknown_token=None, idx_to_token=idx_to_token,
            idx_to_vec=idx_to_vec, unknown_lookup=model)
    else:
        embedding = nlp.embedding.TokenEmbedding.from_file(args.embedding_path)

    return embedding