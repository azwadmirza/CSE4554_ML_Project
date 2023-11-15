def malletmodel2ldamodel(mallet_model, gamma_threshold=0.001, iterations=50):
    """
    Function to convert mallet model to gensim LdaModel. This works by copying the
    training model weights (alpha, beta...) from a trained mallet model into the
    gensim model.

    Args:
        mallet_model : Trained mallet model
        gamma_threshold : To be used for inference in the new LdaModel.
        iterations : number of iterations to be used for inference in the new LdaModel.

    Returns:
        model_gensim : LdaModel instance; copied gensim LdaModel
    """
    model_gensim = LdaModel(
        id2word=mallet_model.id2word, num_topics=mallet_model.num_topics,
        alpha=mallet_model.alpha, iterations=iterations,
        gamma_threshold=gamma_threshold)
    model_gensim.expElogbeta[:] = mallet_model.wordtopics
    return model_gensim