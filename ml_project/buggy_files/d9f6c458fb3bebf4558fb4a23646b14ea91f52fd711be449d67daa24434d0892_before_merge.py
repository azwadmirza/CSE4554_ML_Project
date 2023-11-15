    def _fetch_model(model_name) -> str:

        model_map = {}

        aws_resource_path_v04 = "https://s3.eu-central-1.amazonaws.com/alan-nlp/resources/models-v0.4"
        hu_path: str = "https://nlp.informatik.hu-berlin.de/resources/models"

        model_map["ner"] = "/".join(
            [aws_resource_path_v04, "NER-conll03-english", "en-ner-conll03-v0.4.pt"]
        )

        model_map["ner-fast"] = "/".join(
            [
                aws_resource_path_v04,
                "NER-conll03--h256-l1-b32-p3-0.5-%2Bglove%2Bnews-forward-fast%2Bnews-backward-fast-normal-locked0.5-word0.05--release_4",
                "en-ner-fast-conll03-v0.4.pt",
            ]
        )

        model_map["ner-ontonotes"] = "/".join(
            [
                aws_resource_path_v04,
                "release-ner-ontonotes-0",
                "en-ner-ontonotes-v0.4.pt",
            ]
        )

        model_map["ner-ontonotes-fast"] = "/".join(
            [
                aws_resource_path_v04,
                "release-ner-ontonotes-fast-0",
                "en-ner-ontonotes-fast-v0.4.pt",
            ]
        )

        for key in ["ner-multi", "multi-ner"]:
            model_map[key] = "/".join(
                [
                    aws_resource_path_v04,
                    "release-quadner-512-l2-multi-embed",
                    "quadner-large.pt",
                ]
            )

        for key in ["ner-multi-fast", "multi-ner-fast"]:
            model_map[key] = "/".join(
                [aws_resource_path_v04, "NER-multi-fast", "ner-multi-fast.pt"]
            )

        for key in ["ner-multi-fast-learn", "multi-ner-fast-learn"]:
            model_map[key] = "/".join(
                [
                    aws_resource_path_v04,
                    "NER-multi-fast-evolve",
                    "ner-multi-fast-learn.pt",
                ]
            )

        model_map["upos"] = "/".join(
            [
                aws_resource_path_v04,
                "POS-ontonotes--h256-l1-b32-p3-0.5-%2Bglove%2Bnews-forward%2Bnews-backward-normal-locked0.5-word0.05--v0.4_0",
                "en-pos-ontonotes-v0.4.pt",
            ]
        )

        model_map["pos"] = "/".join(
            [
                hu_path,
                "release-pos-0",
                "en-pos-ontonotes-v0.5.pt",
            ]
        )

        model_map["upos-fast"] = "/".join(
            [
                aws_resource_path_v04,
                "release-pos-fast-0",
                "en-pos-ontonotes-fast-v0.4.pt",
            ]
        )

        model_map["pos-fast"] = "/".join(
            [
                hu_path,
                "release-pos-fast-0",
                "en-pos-ontonotes-fast-v0.5.pt",
            ]
        )

        for key in ["pos-multi", "multi-pos"]:
            model_map[key] = "/".join(
                [
                    aws_resource_path_v04,
                    "release-dodekapos-512-l2-multi",
                    "pos-multi-v0.1.pt",
                ]
            )

        for key in ["pos-multi-fast", "multi-pos-fast"]:
            model_map[key] = "/".join(
                [aws_resource_path_v04, "UPOS-multi-fast", "pos-multi-fast.pt"]
            )

        model_map["frame"] = "/".join(
            [aws_resource_path_v04, "release-frame-1", "en-frame-ontonotes-v0.4.pt"]
        )

        model_map["frame-fast"] = "/".join(
            [
                aws_resource_path_v04,
                "release-frame-fast-0",
                "en-frame-ontonotes-fast-v0.4.pt",
            ]
        )

        model_map["chunk"] = "/".join(
            [
                aws_resource_path_v04,
                "NP-conll2000--h256-l1-b32-p3-0.5-%2Bnews-forward%2Bnews-backward-normal-locked0.5-word0.05--v0.4_0",
                "en-chunk-conll2000-v0.4.pt",
            ]
        )

        model_map["chunk-fast"] = "/".join(
            [
                aws_resource_path_v04,
                "release-chunk-fast-0",
                "en-chunk-conll2000-fast-v0.4.pt",
            ]
        )

        model_map["da-pos"] = "/".join(
            [aws_resource_path_v04, "POS-danish", "da-pos-v0.1.pt"]
        )

        model_map["da-ner"] = "/".join(
            [aws_resource_path_v04, "NER-danish", "da-ner-v0.1.pt"]
        )

        model_map["de-pos"] = "/".join(
            [hu_path, "release-de-pos-0", "de-pos-ud-hdt-v0.5.pt"]
        )

        model_map["de-pos-tweets"] = "/".join(
            [
                aws_resource_path_v04,
                "POS-fine-grained-german-tweets",
                "de-pos-twitter-v0.1.pt",
            ]
        )

        model_map["de-ner"] = "/".join(
            [aws_resource_path_v04, "release-de-ner-0", "de-ner-conll03-v0.4.pt"]
        )

        model_map["de-ner-germeval"] = "/".join(
            [aws_resource_path_v04, "NER-germeval", "de-ner-germeval-0.4.1.pt"]
        )

        model_map["fr-ner"] = "/".join(
            [aws_resource_path_v04, "release-fr-ner-0", "fr-ner-wikiner-0.4.pt"]
        )
        model_map["nl-ner"] = "/".join(
            [aws_resource_path_v04, "NER-conll2002-dutch", "nl-ner-conll02-v0.1.pt"]
        )
        model_map["ml-pos"] = "https://raw.githubusercontent.com/qburst/models-repository/master/FlairMalayalamModels/malayalam-xpos-model.pt"
        model_map["ml-upos"] = "https://raw.githubusercontent.com/qburst/models-repository/master/FlairMalayalamModels/malayalam-upos-model.pt"

        cache_dir = Path("models")
        if model_name in model_map:
            model_name = cached_path(model_map[model_name], cache_dir=cache_dir)

        # the historical German taggers by the @redewiegergabe project
        if model_name == "de-historic-indirect":
            model_file = Path(flair.cache_root)  / cache_dir / 'indirect' / 'final-model.pt'
            if not model_file.exists():
                cached_path('http://www.redewiedergabe.de/models/indirect.zip', cache_dir=cache_dir)
                unzip_file(Path(flair.cache_root)  / cache_dir / 'indirect.zip', Path(flair.cache_root)  / cache_dir)
            model_name = str(Path(flair.cache_root)  / cache_dir / 'indirect' / 'final-model.pt')

        if model_name == "de-historic-direct":
            model_file = Path(flair.cache_root)  / cache_dir / 'direct' / 'final-model.pt'
            if not model_file.exists():
                cached_path('http://www.redewiedergabe.de/models/direct.zip', cache_dir=cache_dir)
                unzip_file(Path(flair.cache_root)  / cache_dir / 'direct.zip', Path(flair.cache_root)  / cache_dir)
            model_name = str(Path(flair.cache_root)  / cache_dir / 'direct' / 'final-model.pt')

        if model_name == "de-historic-reported":
            model_file = Path(flair.cache_root)  / cache_dir / 'reported' / 'final-model.pt'
            if not model_file.exists():
                cached_path('http://www.redewiedergabe.de/models/reported.zip', cache_dir=cache_dir)
                unzip_file(Path(flair.cache_root)  / cache_dir / 'reported.zip', Path(flair.cache_root)  / cache_dir)
            model_name = str(Path(flair.cache_root)  / cache_dir / 'reported' / 'final-model.pt')

        if model_name == "de-historic-free-indirect":
            model_file = Path(flair.cache_root)  / cache_dir / 'freeIndirect' / 'final-model.pt'
            if not model_file.exists():
                cached_path('http://www.redewiedergabe.de/models/freeIndirect.zip', cache_dir=cache_dir)
                unzip_file(Path(flair.cache_root)  / cache_dir / 'freeIndirect.zip', Path(flair.cache_root)  / cache_dir)
            model_name = str(Path(flair.cache_root)  / cache_dir / 'freeIndirect' / 'final-model.pt')

        return model_name