def _collate_best_model(meta, output_path, components):
    bests = {}
    for component in components:
        bests[component] = _find_best(output_path, component)
    best_dest = output_path / "model-best"
    shutil.copytree(output_path / "model-final", best_dest)
    for component, best_component_src in bests.items():
        shutil.rmtree(best_dest / component)
        shutil.copytree(best_component_src / component, best_dest / component)
        accs = srsly.read_json(best_component_src / "accuracy.json")
        for metric in _get_metrics(component):
            meta["accuracy"][metric] = accs[metric]
    srsly.write_json(best_dest / "meta.json", meta)
    return best_dest