    def __init__(self, xml, encoding_errors="strict"):
        self.xml_dom = MediaInfo._parse_xml_data_into_dom(xml, encoding_errors)