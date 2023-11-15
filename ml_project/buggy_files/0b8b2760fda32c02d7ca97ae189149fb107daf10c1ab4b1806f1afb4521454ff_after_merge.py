def vwmodel2ldamodel(vw_model, iterations=50):
    """
    Function to convert vowpal wabbit model to gensim LdaModel. This works by
    simply copying the training model weights (alpha, beta...) from a trained
    vwmodel into the gensim model.

    Args:
        vw_model : Trained vowpal wabbit model.
        iterations : Number of iterations to be used for inference of the new LdaModel.

    Returns:
        model_gensim : LdaModel instance; copied gensim LdaModel.
    """
    model_gensim = LdaModel(
        num_topics=vw_model.num_topics, id2word=vw_model.id2word, chunksize=vw_model.chunksize,
        passes=vw_model.passes, alpha=vw_model.alpha, eta=vw_model.eta, decay=vw_model.decay,
        offset=vw_model.offset, iterations=iterations, gamma_threshold=vw_model.gamma_threshold)
    model_gensim.expElogbeta[:] = vw_model._get_topics()
    return model_gensim