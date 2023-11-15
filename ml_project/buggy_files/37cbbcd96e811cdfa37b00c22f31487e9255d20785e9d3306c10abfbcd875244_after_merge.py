def parse_json_main_index(out_dir: str=OUTPUT_DIR) -> Iterator[Link]:
    """parse an archive index json file and return the list of links"""

    index_path = os.path.join(out_dir, JSON_INDEX_FILENAME)
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            links = pyjson.load(f)['links']
            for link_json in links:
                try:
                    yield Link.from_json(link_json)
                except KeyError:
                    try:
                        detail_index_path = Path(OUTPUT_DIR) / ARCHIVE_DIR_NAME / link_json['timestamp']
                        yield parse_json_link_details(str(detail_index_path))
                    except KeyError: 
                        print("    {lightyellow}! Failed to load the index.json from {}".format(detail_index_path, **ANSI))
                        continue
    return ()