def create_title(plugin=None):
    if args.title and plugin:
        title = LazyFormatter.format(
            maybe_encode(args.title),
            title=lambda: plugin.get_title() or DEFAULT_STREAM_METADATA["title"],
            author=lambda: plugin.get_author() or DEFAULT_STREAM_METADATA["author"],
            category=lambda: plugin.get_category() or DEFAULT_STREAM_METADATA["category"],
            game=lambda: plugin.get_category() or DEFAULT_STREAM_METADATA["game"],
            url=plugin.url
        )
    else:
        title = args.url
    return title