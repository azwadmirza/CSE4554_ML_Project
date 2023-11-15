    def _fetch_model(model_name) -> str:

        model_map = {}
        hu_path: str = "https://nlp.informatik.hu-berlin.de/resources/models"

        model_map["de-offensive-language"] = "/".join(
            [hu_path, "de-offensive-language", "germ-eval-2018-task-1-v0.4.pt"]
        )

        # English sentiment models
        model_map["sentiment"] = "/".join(
            [hu_path, "sentiment-curated-distilbert", "sentiment-en-mix-distillbert.pt"]
        )
        model_map["en-sentiment"] = "/".join(
            [hu_path, "sentiment-curated-distilbert", "sentiment-en-mix-distillbert.pt"]
        )
        model_map["sentiment-fast"] = "/".join(
            [hu_path, "sentiment-curated-fasttext-rnn", "sentiment-en-mix-ft-rnn.pt"]
        )
        
        #Communicative Functions Model
        model_map["communicative-functions"] = "/".join(
            [hu_path, "comfunc", "communicative-functions-v0.5b.pt"]
        )

        cache_dir = Path("models")
        if model_name in model_map:
            model_name = cached_path(model_map[model_name], cache_dir=cache_dir)

        return model_name