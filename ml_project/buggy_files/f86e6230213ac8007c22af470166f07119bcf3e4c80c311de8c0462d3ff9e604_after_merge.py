    def predict(self, question: str, documents: List[Document], top_k: Optional[int] = None) -> Dict:
        """
        Generate the answer to the input question. The generation will be conditioned on the supplied documents.
        These document can for example be retrieved via the Retriever.

        :param question: Question
        :param documents: Related documents (e.g. coming from a retriever) that the answer shall be conditioned on.
        :param top_k: Number of returned answers
        :return: Generated answers plus additional infos in a dict like this:

        ```python
        > {'question': 'who got the first nobel prize in physics',
        >    'answers':
        >        [{'question': 'who got the first nobel prize in physics',
        >          'answer': ' albert einstein',
        >          'meta': { 'doc_ids': [...],
        >                    'doc_scores': [80.42758 ...],
        >                    'doc_probabilities': [40.71379089355469, ...
        >                    'texts': ['Albert Einstein was a ...]
        >                    'titles': ['"Albert Einstein"', ...]
        >    }}]}
        ```
        """
        if len(documents) == 0:
            raise AttributeError("generator need documents to predict the answer")

        top_k_answers = top_k if top_k is not None else self.top_k_answers

        if top_k_answers > self.num_beams:
            top_k_answers = self.num_beams
            logger.warning(f'top_k_answers value should not be greater than num_beams, '
                           f'hence setting it to {top_k_answers}')

        # Flatten the documents so easy to reference
        flat_docs_dict: Dict[str, Any] = {}
        for document in documents:
            for k, v in document.__dict__.items():
                if k not in flat_docs_dict:
                    flat_docs_dict[k] = []
                flat_docs_dict[k].append(v)

        # Extract title
        titles = [d.meta["name"] if d.meta and "name" in d.meta else "" for d in documents]

        # Raw document embedding and set device of question_embedding
        passage_embeddings = self._prepare_passage_embeddings(docs=documents, embeddings=flat_docs_dict["embedding"])

        # Question tokenization
        input_dict = self.tokenizer.prepare_seq2seq_batch(
            src_texts=[question],
            return_tensors="pt"
        )

        # Question embedding
        question_embedding = self.model.question_encoder(input_dict["input_ids"])[0]

        # Prepare contextualized input_ids of documents
        # (will be transformed into contextualized inputs inside generator)
        context_input_ids, context_attention_mask = self._get_contextualized_inputs(
            texts=flat_docs_dict["text"],
            titles=titles,
            question=question
        )

        # Compute doc scores from docs_embedding
        doc_scores = torch.bmm(question_embedding.unsqueeze(1),
                               passage_embeddings.unsqueeze(0).transpose(1, 2)).squeeze(1)

        # TODO Need transformers 3.4.0
        # Refer https://github.com/huggingface/transformers/issues/7874
        # Pass it as parameter to generate function as follows -
        # n_docs=len(flat_docs_dict["text"])
        self.model.config.n_docs = len(flat_docs_dict["text"])

        # Get generated ids from generator
        generator_ids = self.model.generate(
            # TODO: Need transformers 3.4.0
            # Refer https://github.com/huggingface/transformers/issues/7871
            # Remove input_ids parameter once upgraded to 3.4.0
            input_ids=input_dict["input_ids"],
            context_input_ids=context_input_ids,
            context_attention_mask=context_attention_mask,
            doc_scores=doc_scores,
            num_return_sequences=top_k_answers,
            num_beams=self.num_beams,
            max_length=self.max_length,
            min_length=self.min_length,
        )

        generated_answers = self.tokenizer.batch_decode(generator_ids, skip_special_tokens=True)
        answers: List[Any] = []

        for generated_answer in generated_answers:
            cur_answer = {
                "question": question,
                "answer": generated_answer,
                "meta": {
                    "doc_ids": flat_docs_dict["id"],
                    "doc_scores": flat_docs_dict["score"],
                    "doc_probabilities": flat_docs_dict["probability"],
                    "texts": flat_docs_dict["text"],
                    "titles": titles,
                }
            }
            answers.append(cur_answer)

        result = {"question": question, "answers": answers}

        return result