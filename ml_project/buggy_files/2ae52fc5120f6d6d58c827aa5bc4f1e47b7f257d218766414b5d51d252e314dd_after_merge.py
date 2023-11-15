def replace_text_feature_level(model_definition, datasets):
    for feature in (model_definition['input_features'] +
                    model_definition['output_features']):
        if feature['type'] == TEXT:
            for dataset in datasets:
                dataset[feature['name']] = dataset[
                    '{}_{}'.format(
                        feature['name'],
                        feature['level']
                    )
                ]
                for level in ('word', 'char'):
                    name_level = '{}_{}'.format(
                            feature['name'],
                            level)
                    if name_level in dataset:
                        del dataset[name_level]