def parse_json_main_index(out_dir: str=OUTPUT_DIR) -> Iterator[Link]:
    """parse an archive index json file and return the list of links"""

    index_path = os.path.join(out_dir, JSON_INDEX_FILENAME)
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            links = pyjson.load(f)['links']
            for link_json in links:
                yield Link.from_json(link_json)

    return ()