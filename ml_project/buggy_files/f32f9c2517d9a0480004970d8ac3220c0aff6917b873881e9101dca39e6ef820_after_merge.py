def _apply_model(nlp):
    for text, annotation in TRAIN_DATA:
        # apply the entity linker which will now make predictions for the 'Russ Cochran' entities
        doc = nlp(text)
        print()
        print("Entities", [(ent.text, ent.label_, ent.kb_id_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_kb_id_) for t in doc])