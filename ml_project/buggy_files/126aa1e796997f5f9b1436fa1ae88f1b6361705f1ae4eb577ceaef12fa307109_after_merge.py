    def write_labels(self, labels, index=None):

        labels = [Label.from_dict(l) if isinstance(l, dict) else l for l in labels]
        index = index or self.index
        for label in labels:
            label_orm = LabelORM(
                id=str(uuid4()),
                document_id=label.document_id,
                no_answer=label.no_answer,
                origin=label.origin,
                question=label.question,
                is_correct_answer=label.is_correct_answer,
                is_correct_document=label.is_correct_document,
                answer=label.answer,
                offset_start_in_doc=label.offset_start_in_doc,
                model_id=label.model_id,
                index=index,
            )
            self.session.add(label_orm)
        self.session.commit()