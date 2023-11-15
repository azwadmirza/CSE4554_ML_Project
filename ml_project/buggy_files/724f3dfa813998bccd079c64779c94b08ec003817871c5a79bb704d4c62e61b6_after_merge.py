def build_bow_text_classifier(nr_class, ngram_size=1, exclusive_classes=False,
        no_output_layer=False, **cfg):
    with Model.define_operators({">>": chain}):
        model = (
            with_cpu(Model.ops,
                extract_ngrams(ngram_size, attr=ORTH) 
                >> LinearModel(nr_class)
            )
        )
        if not no_output_layer:
            model = model >> (cpu_softmax if exclusive_classes else logistic)
    model.nO = nr_class
    return model