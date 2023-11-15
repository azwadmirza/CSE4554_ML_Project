def register(input_channels: List['InputChannel'],
             app: Flask,
             on_new_message: Callable[[UserMessage], None],
             route: Text
             ) -> None:
    for channel in input_channels:
        p = urljoin(route, channel.url_prefix())
        app.register_blueprint(channel.blueprint(on_new_message), url_prefix=p)