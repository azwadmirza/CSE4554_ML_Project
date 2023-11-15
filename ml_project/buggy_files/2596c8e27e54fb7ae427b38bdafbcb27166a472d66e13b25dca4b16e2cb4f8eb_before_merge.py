    def _lm_specific_token_cleanup(self, token_strings: List[Text]) -> List[Text]:
        from rasa.nlu.utils.hugging_face.registry import model_tokens_cleaners

        return model_tokens_cleaners[self.model_name](token_strings)