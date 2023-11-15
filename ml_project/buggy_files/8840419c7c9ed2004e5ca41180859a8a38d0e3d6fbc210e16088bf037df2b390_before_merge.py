    def __init__(self, question: str,
                 answer: str,
                 is_correct_answer: bool,
                 is_correct_document: bool,
                 origin: str,
                 document_id: Optional[UUID] = None,
                 offset_start_in_doc: Optional[int] = None,
                 no_answer: Optional[bool] = None,
                 model_id: Optional[int] = None):
        """
        Object used to represent label/feedback in a standardized way within Haystack.
        This includes labels from dataset like SQuAD, annotations from labeling tools,
        or, user-feedback from the Haystack REST API.

        :param question: the question(or query) for finding answers.
        :param answer: teh answer string.
        :param is_correct_answer: whether the sample is positive or negative.
        :param is_correct_document: in case of negative sample(is_correct_answer is False), there could be two cases;
                                    incorrect answer but correct document & incorrect document. This flag denotes if
                                    the returned document was correct.
        :param origin: the source for the labels. It can be used to later for filtering.
        :param document_id: the document_store's ID for the returned answer document.
        :param offset_start_in_doc: the answer start offset in the document.
        :param no_answer: whether the question in unanswerable.
        :param model_id: model_id used for prediction(in-case of user feedback).
        """
        self.no_answer = no_answer
        self.origin = origin
        self.question = question
        self.is_correct_answer = is_correct_answer
        self.is_correct_document = is_correct_document
        if document_id:
            if isinstance(document_id, str):
                self.document_id: Optional[UUID] = UUID(hex=str(document_id), version=4)
            if isinstance(document_id, UUID):
                self.document_id = document_id
        else:
            self.document_id = document_id
        self.answer = answer
        self.offset_start_in_doc = offset_start_in_doc
        self.model_id = model_id