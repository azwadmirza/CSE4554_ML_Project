    def __setstate__(self, d):
        self.__dict__ = d

        # necessary for reverse compatibility with Flair <= 0.7
        if 'use_scalar_mix' in self.__dict__.keys():
            self.__dict__['layer_mean'] = d['use_scalar_mix']
        if not 'memory_effective_training' in self.__dict__.keys():
            self.__dict__['memory_effective_training'] = True
        if 'pooling_operation' in self.__dict__.keys():
            self.__dict__['subtoken_pooling'] = d['pooling_operation']
        if not 'context_length' in self.__dict__.keys():
            self.__dict__['context_length'] = 0
        if 'use_context' in self.__dict__.keys():
            self.__dict__['context_length'] = 64 if self.__dict__['use_context'] == True else 0

        if not 'respect_document_boundaries' in self.__dict__.keys():
            self.__dict__['respect_document_boundaries'] = True
        if not 'memory_effective_training' in self.__dict__.keys():
            self.__dict__['memory_effective_training'] = True

        # constructor arguments
        layers = ','.join([str(idx) for idx in self.__dict__['layer_indexes']])
        subtoken_pooling = self.__dict__['subtoken_pooling']
        context_length = self.__dict__['context_length']
        layer_mean = self.__dict__['layer_mean']
        fine_tune = self.__dict__['fine_tune']
        allow_long_sentences = self.__dict__['allow_long_sentences']
        respect_document_boundaries = self.__dict__['respect_document_boundaries']
        memory_effective_training = self.__dict__['memory_effective_training']

        model_name = self.__dict__['name'].split('transformer-word-')[-1]

        # special handling for deserializing transformer models
        if "config_state_dict" in d:

            # load transformer model
            config_class = CONFIG_MAPPING[d["config_state_dict"]["model_type"]]
            loaded_config = config_class.from_dict(d["config_state_dict"])

            # re-initialize transformer word embeddings with constructor arguments
            embedding = TransformerWordEmbeddings(model_name,
                                              layers=layers,
                                              subtoken_pooling=subtoken_pooling,
                                              use_context=context_length,
                                              layer_mean=layer_mean,
                                              fine_tune=fine_tune,
                                              allow_long_sentences=allow_long_sentences,
                                              respect_document_boundaries=respect_document_boundaries,
                                              memory_effective_training=memory_effective_training,
                                              config=loaded_config,
                                              state_dict=d["model_state_dict"],
                                              )

            # I have no idea why this is necessary, but otherwise it doesn't work
            for key in embedding.__dict__.keys():
                self.__dict__[key] = embedding.__dict__[key]

        else:

            # reload tokenizer to get around serialization issues
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_name)

            except:
                pass

            self.tokenizer = tokenizer