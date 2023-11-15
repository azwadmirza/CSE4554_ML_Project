    def query_by_embedding(self,
                           query_emb: np.array,
                           filters: Optional[Dict[str, List[str]]] = None,
                           top_k: int = 10,
                           index: Optional[str] = None) -> List[Document]:
        if index is None:
            index = self.index

        if not self.embedding_field:
            raise RuntimeError("Please specify arg `embedding_field` in ElasticsearchDocumentStore()")
        else:
            # +1 in similarity to avoid negative numbers (for cosine sim)
            body= {
                "size": top_k,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            # offset score to ensure a positive range as required by Elasticsearch
                            "source": f"{self.similarity_fn_name}(params.query_vector,'{self.embedding_field}') + 1000",
                            "params": {
                                "query_vector": query_emb.tolist()
                            }
                        }
                    }
                }
            }  # type: Dict[str,Any]

            if filters:
                for key, values in filters.items():
                    if type(values) != list:
                        raise ValueError(f'Wrong filter format for key "{key}": Please provide a list of allowed values for each key. '
                                         'Example: {"name": ["some", "more"], "category": ["only_one"]} ')
                body["query"]["script_score"]["query"] = {
                    "terms": filters
                }

            if self.excluded_meta_data:
                body["_source"] = {"excludes": self.excluded_meta_data}

            logger.debug(f"Retriever query: {body}")
            result = self.client.search(index=index, body=body, request_timeout=300)["hits"]["hits"]

            documents = [self._convert_es_hit_to_document(hit, adapt_score_for_embedding=True) for hit in result]
            return documents