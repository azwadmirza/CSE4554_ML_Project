def register(input_channels: List['InputChannel'],
             app: Flask,
             on_new_message: Callable[[UserMessage], None],
             route: Optional[Text]
             ) -> None:
    for channel in input_channels:
        if route:
            p = urljoin(route, channel.url_prefix())
        else:
            p = None

        app.register_blueprint(channel.blueprint(on_new_message), url_prefix=p)