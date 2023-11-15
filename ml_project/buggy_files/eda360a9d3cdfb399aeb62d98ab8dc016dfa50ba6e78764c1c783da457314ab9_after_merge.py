    def _init(self):
        self.extractors = [Extractor(label=self.label,
                        path="//div[@id='main']//div[1]//div//table//tbody//tr",
                        attrs=Attribute(key=None,
                                multi=True,
                                path={self.ranktext: "./td[2]//text()",
                                        'rating': "./td[3]//strong//text()",
                                        'title': "./td[2]//a//text()",
                                        'year': "./td[2]//span//text()",
                                        'movieID': "./td[2]//a/@href",
                                        'votes': "./td[3]//strong/@title"
                                        }))]