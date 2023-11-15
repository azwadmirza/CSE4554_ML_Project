    def __call__(self, data, **metadata):
        data = data.decode("utf-8")
        h = html2text.HTML2Text(baseurl="")
        h.ignore_images = True
        h.body_width = 0
        outline = h.handle(data)
        return "HTML Outline", format_text(outline)