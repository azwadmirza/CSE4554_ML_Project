    def _init(self):
        self.extractors = [Extractor(label=self.label,
                        path="//div[@id='main']//table//tr",
                        attrs=Attribute(key=None,
                                multi=True,
                                path={self.ranktext: "./td[1]//text()",
                                        'rating': "./td[2]//text()",
                                        'title': "./td[3]//text()",
                                        'movieID': "./td[3]//a/@href",
                                        'votes': "./td[4]//text()"
                                        }))]