    def _convert_es_hit_to_document(self, hit: dict, adapt_score_for_embedding: bool = False) -> Document:
        # We put all additional data of the doc into meta_data and return it in the API
        meta_data = {k:v for k,v in hit["_source"].items() if k not in (self.text_field, self.faq_question_field, self.embedding_field)}
        name = meta_data.pop(self.name_field, None)
        if name:
            meta_data["name"] = name

        score = hit["_score"] if hit["_score"] else None
        if score:
            if adapt_score_for_embedding:
                score -= 1
                probability = (score + 1) / 2  # scaling probability from cosine similarity
            else:
                probability = float(expit(np.asarray(score / 8)))  # scaling probability from TFIDF/BM25
        else:
            probability = None
        document = Document(
            id=hit["_id"],
            text=hit["_source"].get(self.text_field),
            meta=meta_data,
            score=score,
            probability=probability,
            question=hit["_source"].get(self.faq_question_field),
            embedding=hit["_source"].get(self.embedding_field)
        )
        return document