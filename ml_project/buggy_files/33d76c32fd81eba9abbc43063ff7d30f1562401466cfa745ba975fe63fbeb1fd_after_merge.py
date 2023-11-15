def init_model(lang, output_dir, freqs_loc, clusters_loc=None, vectors_loc=None, prune_vectors=-1):
    """
    Create a new model from raw data, like word frequencies, Brown clusters
    and word vectors.
    """
    if not freqs_loc.exists():
        prints(freqs_loc, title="Can't find words frequencies file", exits=1)
    clusters_loc = ensure_path(clusters_loc)
    vectors_loc = ensure_path(vectors_loc)

    probs, oov_prob = read_freqs(freqs_loc)
    vectors_data, vector_keys = read_vectors(vectors_loc) if vectors_loc else (None, None)
    clusters = read_clusters(clusters_loc) if clusters_loc else {}

    nlp = create_model(lang, probs, oov_prob, clusters, vectors_data, vector_keys, prune_vectors)

    if not output_dir.exists():
        output_dir.mkdir()
    nlp.to_disk(output_dir)
    return nlp