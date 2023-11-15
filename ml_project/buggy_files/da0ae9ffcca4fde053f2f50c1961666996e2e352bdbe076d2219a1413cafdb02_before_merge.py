    def convert_to_transformers(self):
        if len(self.prediction_heads) != 1:
            raise ValueError(f"Currently conversion only works for models with a SINGLE prediction head. "
                             f"Your model has {len(self.prediction_heads)}")
        elif len(self.prediction_heads[0].layer_dims) != 2:
            raise ValueError(f"Currently conversion only works for PredictionHeads that are a single layer Feed Forward NN with dimensions [LM_output_dim, number_classes].\n"
                             f"            Your PredictionHead has {str(self.prediction_heads[0].layer_dims)} dimensions.")
        #TODO add more infos to config

        if self.prediction_heads[0].model_type == "span_classification":
            # init model
            transformers_model = AutoModelForQuestionAnswering.from_config(self.language_model.model.config)
            # transfer weights for language model + prediction head
            setattr(transformers_model, transformers_model.base_model_prefix, self.language_model.model)
            transformers_model.qa_outputs.load_state_dict(
                self.prediction_heads[0].feed_forward.feed_forward[0].state_dict())

        elif self.prediction_heads[0].model_type == "language_modelling":
            # init model
            transformers_model = AutoModelWithLMHead.from_config(self.language_model.model.config)
            # transfer weights for language model + prediction head
            setattr(transformers_model, transformers_model.base_model_prefix, self.language_model.model)
            ph_state_dict = self.prediction_heads[0].state_dict()
            ph_state_dict["transform.dense.weight"] = ph_state_dict.pop("dense.weight")
            ph_state_dict["transform.dense.bias"] = ph_state_dict.pop("dense.bias")
            ph_state_dict["transform.LayerNorm.weight"] = ph_state_dict.pop("LayerNorm.weight")
            ph_state_dict["transform.LayerNorm.bias"] = ph_state_dict.pop("LayerNorm.bias")
            transformers_model.cls.predictions.load_state_dict(ph_state_dict)
            logger.warning("Currently only the Masked Language Modeling component of the prediction head is converted, "
                           "not the Next Sentence Prediction or Sentence Order Prediction components")

        elif self.prediction_heads[0].model_type == "text_classification":
            if self.language_model.model.base_model_prefix == "roberta":
                # Classification Heads in transformers have different architecture across Language Model variants
                # The RobertaClassificationhead has components: input2dense, dropout, tanh, dense2output
                # The tanh function cannot be mapped to current FARM style linear Feed Forward ClassificationHeads.
                # So conversion for this type cannot work. We would need a compatible FARM RobertaClassificationHead
                logger.error("Conversion for Text Classification with Roberta or XLMRoberta not possible at the moment.")
                raise NotImplementedError

            # add more info to config
            self.language_model.model.config.id2label = {id: label for id, label in enumerate(self.prediction_heads[0].label_list)}
            self.language_model.model.config.label2id = {label: id for id, label in enumerate(self.prediction_heads[0].label_list)}
            self.language_model.model.config.finetuning_task = "text_classification"
            self.language_model.model.config.language = self.language_model.language
            self.language_model.model.config.num_labels = self.prediction_heads[0].num_labels

            # init model
            transformers_model = AutoModelForSequenceClassification.from_config(self.language_model.model.config)
            # transfer weights for language model + prediction head
            setattr(transformers_model, transformers_model.base_model_prefix, self.language_model.model)
            transformers_model.classifier.load_state_dict(
                self.prediction_heads[0].feed_forward.feed_forward[0].state_dict())
        elif self.prediction_heads[0].model_type == "token_classification":
            # add more info to config
            self.language_model.model.config.id2label = {id: label for id, label in enumerate(self.prediction_heads[0].label_list)}
            self.language_model.model.config.label2id = {label: id for id, label in enumerate(self.prediction_heads[0].label_list)}
            self.language_model.model.config.finetuning_task = "token_classification"
            self.language_model.model.config.language = self.language_model.language
            self.language_model.model.config.num_labels = self.prediction_heads[0].num_labels

            # init model
            transformers_model = AutoModelForTokenClassification.from_config(self.language_model.model.config)
            # transfer weights for language model + prediction head
            setattr(transformers_model, transformers_model.base_model_prefix, self.language_model.model)
            transformers_model.classifier.load_state_dict(
                self.prediction_heads[0].feed_forward.feed_forward[0].state_dict())
        else:
            raise NotImplementedError(f"FARM -> Transformers conversion is not supported yet for"
                                      f" prediction heads of type {self.prediction_heads[0].model_type}")
        pass

        return transformers_model