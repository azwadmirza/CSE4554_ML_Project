    def __init__(self, filename):
        with translate_errors():
            audio = MP4(filename)
        self["~codec"] = getattr(audio.info, "codec_description", u"AAC")
        self["~#length"] = audio.info.length
        self["~#bitrate"] = int(audio.info.bitrate / 1000)

        for key, values in audio.items():
            if key in self.__tupletranslate:
                if values:
                    name = self.__tupletranslate[key]
                    cur, total = values[0]
                    if total:
                        self[name] = u"%d/%d" % (cur, total)
                    else:
                        self[name] = text_type(cur)
            elif key in self.__translate:
                name = self.__translate[key]
                if key == "tmpo":
                    self[name] = u"\n".join(map(text_type, values))
                elif key.startswith("----"):
                    self[name] = "\n".join(
                        map(lambda v: decode(v).strip("\x00"), values))
                else:
                    self[name] = "\n".join(values)
            elif key == "covr":
                self.has_images = True
        self.sanitize(filename)