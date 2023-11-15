def _apply_model(nlp):
    for text, annotation in TRAIN_DATA:
        doc = nlp.tokenizer(text)

        # set entities so the evaluation is independent of the NER step
        # all the examples contain 'Russ Cochran' as the first two tokens in the sentence
        rc_ent = Span(doc, 0, 2, label=PERSON)
        doc.ents = [rc_ent]

        # apply the entity linker which will now make predictions for the 'Russ Cochran' entities
        doc = nlp.get_pipe("entity_linker")(doc)

        print()
        print("Entities", [(ent.text, ent.label_, ent.kb_id_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_kb_id_) for t in doc])