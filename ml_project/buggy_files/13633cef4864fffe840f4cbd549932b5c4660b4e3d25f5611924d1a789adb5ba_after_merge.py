def _populate():
    for fname in glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*.json')):
        with open(fname, encoding="utf-8") as inf:
            data = json.load(inf)
            data = data[list(data.keys())[0]]
            data = data[list(data.keys())[0]]
            for item in data:
                if item['key'] in TABLE:
                    LOGGER.warning('Repeated emoji {}'.format(item['key']))
                else:
                    TABLE[item['key']] = item['value']