def main(kb_path, vocab_path=None, output_dir=None, n_iter=50):
    """Create a blank model with the specified vocab, set up the pipeline and train the entity linker.
    The `vocab` should be the one used during creation of the KB."""
    vocab = Vocab().from_disk(vocab_path)
    # create blank Language class with correct vocab
    nlp = spacy.blank("en", vocab=vocab)
    nlp.vocab.vectors.name = "spacy_pretrained_vectors"
    print("Created blank 'en' model with vocab from '%s'" % vocab_path)

    # Add a sentencizer component. Alternatively, add a dependency parser for higher accuracy.
    nlp.add_pipe(nlp.create_pipe('sentencizer'))

    # Add a custom component to recognize "Russ Cochran" as an entity for the example training data.
    # Note that in a realistic application, an actual NER algorithm should be used instead.
    ruler = EntityRuler(nlp)
    patterns = [{"label": "PERSON", "pattern": [{"LOWER": "russ"}, {"LOWER": "cochran"}]}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)

    # Create the Entity Linker component and add it to the pipeline.
    if "entity_linker" not in nlp.pipe_names:
        # use only the predicted EL score and not the prior probability (for demo purposes)
        cfg = {"incl_prior": False}
        entity_linker = nlp.create_pipe("entity_linker", cfg)
        kb = KnowledgeBase(vocab=nlp.vocab)
        kb.load_bulk(kb_path)
        print("Loaded Knowledge Base from '%s'" % kb_path)
        entity_linker.set_kb(kb)
        nlp.add_pipe(entity_linker, last=True)

    # Convert the texts to docs to make sure we have doc.ents set for the training examples.
    # Also ensure that the annotated examples correspond to known identifiers in the knowlege base.
    kb_ids = nlp.get_pipe("entity_linker").kb.get_entity_strings()
    TRAIN_DOCS = []
    for text, annotation in TRAIN_DATA:
        with nlp.disable_pipes("entity_linker"):
            doc = nlp(text)
        annotation_clean = annotation
        for offset, kb_id_dict in annotation["links"].items():
            new_dict = {}
            for kb_id, value in kb_id_dict.items():
                if kb_id in kb_ids:
                    new_dict[kb_id] = value
                else:
                    print(
                        "Removed", kb_id, "from training because it is not in the KB."
                    )
            annotation_clean["links"][offset] = new_dict
        TRAIN_DOCS.append((doc, annotation_clean))

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "entity_linker"]
    with nlp.disable_pipes(*other_pipes):  # only train entity linker
        # reset and initialize the weights randomly
        optimizer = nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DOCS)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DOCS, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.2,  # dropout - make it harder to memorise data
                    losses=losses,
                    sgd=optimizer,
                )
            print(itn, "Losses", losses)

    # test the trained model
    _apply_model(nlp)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print()
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        _apply_model(nlp2)