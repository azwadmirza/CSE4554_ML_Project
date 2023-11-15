def load_embedding_from_path(args):
    """Load a TokenEmbedding."""
    if args.embedding_path.endswith('.bin'):
        with utils.print_time('load fastText model.'):
            model = \
                nlp.model.train.FasttextEmbeddingModel.load_fasttext_format(
                    args.embedding_path)
        idx_to_token = sorted(model._token_to_idx, key=model._token_to_idx.get)

        embedding = nlp.embedding.TokenEmbedding(
            unknown_token=None, unknown_lookup=model, allow_extend=True)

        # Analogy task is open-vocabulary, so must keep all known words.
        # But if not evaluating analogy, no need to precompute now as all
        # words for closed vocabulary task can be obtained via the unknown
        # lookup
        if not args.analogy_datasets:
            idx_to_token = []
        elif args.analogy_datasets and args.analogy_max_vocab_size:
            idx_to_token = idx_to_token[:args.analogy_max_vocab_size]

        embedding['<unk>'] = mx.nd.zeros(model.weight.shape[1])
        if idx_to_token:
            with utils.print_time('compute vectors for {} known '
                                  'words.'.format(len(idx_to_token))):
                embedding[idx_to_token] = model[idx_to_token]
    else:
        embedding = nlp.embedding.TokenEmbedding.from_file(args.embedding_path)

    return embedding