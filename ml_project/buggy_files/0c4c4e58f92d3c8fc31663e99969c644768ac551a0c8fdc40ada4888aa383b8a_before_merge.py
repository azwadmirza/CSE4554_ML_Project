    def __init__(self, xml, encoding_errors="strict"):
        xml_dom = ET.fromstring(xml.encode("utf-8", encoding_errors))
        self.tracks = []
        # This is the case for libmediainfo < 18.03
        # https://github.com/sbraz/pymediainfo/issues/57
        # https://github.com/MediaArea/MediaInfoLib/commit/575a9a32e6960ea34adb3bc982c64edfa06e95eb
        if xml_dom.tag == "File":
            xpath = "track"
        else:
            xpath = "File/track"
        for xml_track in xml_dom.iterfind(xpath):
            self.tracks.append(Track(xml_track))