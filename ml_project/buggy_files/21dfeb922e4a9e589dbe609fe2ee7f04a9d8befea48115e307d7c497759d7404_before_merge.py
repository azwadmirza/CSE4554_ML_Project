    def write(self):
        with translate_errors():
            audio = self.Kind(self['~filename'])

        if audio.tags is None:
            audio.add_tags()
        tag = audio.tags

        # prefill TMCL with the ones we can't read
        mcl = tag.get("TMCL", mutagen.id3.TMCL(encoding=3, people=[]))
        mcl.people = [(r, n) for (r, n) in mcl.people
                      if not self.__validate_name(r)]

        # delete all TXXX/COMM we can read except empty COMM
        for frame in ["COMM:", "TXXX:"]:
            for t in tag.getall(frame + "QuodLibet:"):
                if t.desc and self.__validate_name(t.desc):
                    del tag[t.HashKey]

        for key in ["UFID:http://musicbrainz.org",
                    "TMCL",
                    "POPM:%s" % const.EMAIL,
                    "POPM:%s" % config.get("editing", "save_email")]:
            if key in tag:
                del(tag[key])

        for key, id3name in self.SDI.items():
            tag.delall(id3name)
            if key not in self:
                continue
            enc = encoding_for(self[key])
            Kind = mutagen.id3.Frames[id3name]
            text = self[key].split("\n")
            if id3name == "WOAR":
                for t in text:
                    tag.add(Kind(url=t))
            else:
                tag.add(Kind(encoding=enc, text=text))

        dontwrite = ["genre", "comment", "musicbrainz_trackid", "lyrics"] \
            + RG_KEYS + listvalues(self.TXXX_MAP)

        if "musicbrainz_trackid" in self.realkeys():
            f = mutagen.id3.UFID(
                owner="http://musicbrainz.org",
                data=self["musicbrainz_trackid"].encode("utf-8"))
            tag.add(f)

        # Issue 439 - Only write valid ISO 639-2 codes to TLAN (else TXXX)
        tag.delall("TLAN")
        if "language" in self:
            langs = self["language"].split("\n")
            if all([lang in ISO_639_2 for lang in langs]):
                # Save value(s) to TLAN tag. Guaranteed to be ASCII here
                tag.add(mutagen.id3.TLAN(encoding=3, text=langs))
                dontwrite.append("language")
            else:
                print_d("Not using invalid language code '%s' in TLAN" %
                        self["language"])

        # Filter out known keys, and ones set not to write [generically].
        keys_to_write = filter(lambda k: not (k in self.SDI or k in dontwrite),
                               self.realkeys())
        for key in keys_to_write:
            enc = encoding_for(self[key])
            if key.startswith("performer:"):
                mcl.people.append([key.split(":", 1)[1], self[key]])
                continue

            f = mutagen.id3.TXXX(
                encoding=enc, text=self[key].split("\n"),
                desc=u"QuodLibet::%s" % key)
            tag.add(f)

        if mcl.people:
            tag.add(mcl)

        if "genre" in self:
            enc = encoding_for(self["genre"])
            t = self["genre"].split("\n")
            tag.add(mutagen.id3.TCON(encoding=enc, text=t))
        else:
            try:
                del(tag["TCON"])
            except KeyError:
                pass

        tag.delall("COMM:")
        if "comment" in self:
            enc = encoding_for(self["comment"])
            t = self["comment"].split("\n")
            tag.add(mutagen.id3.COMM(encoding=enc, text=t, desc=u"",
                                     lang="\x00\x00\x00"))

        tag.delall("USLT::\x00\x00\x00")
        if "lyrics" in self:
            enc = encoding_for(self["lyrics"])
            # lyrics are single string, not array
            tag.add(mutagen.id3.USLT(encoding=enc, text=self["lyrics"],
                                     desc=u"", lang="\x00\x00\x00"))

        # Delete old foobar replaygain ..
        for frame in tag.getall("TXXX"):
            if frame.desc.lower() in RG_KEYS:
                del tag[frame.HashKey]

        # .. write new one
        for k in RG_KEYS:
            # Add new ones
            if k in self:
                value = self[k]
                tag.add(mutagen.id3.TXXX(encoding=encoding_for(value),
                                         text=value.split("\n"),
                                         desc=k))

        # we shouldn't delete all, but we use unknown ones as fallback, so make
        # sure they don't come back after reloading
        for t in tag.getall("RVA2"):
            if t.channel == 1:
                del tag[t.HashKey]

        for k in ["track", "album"]:
            if ('replaygain_%s_gain' % k) in self:
                try:
                    gain = float(self["replaygain_%s_gain" % k].split()[0])
                except ValueError:
                    gain = 0
                try:
                    peak = float(self["replaygain_%s_peak" % k])
                except (ValueError, KeyError):
                    peak = 0
                # https://github.com/quodlibet/quodlibet/issues/1027
                peak = max(min(1.9, peak), 0)
                gain = max(min(63.9, gain), -64)
                f = mutagen.id3.RVA2(desc=k, channel=1, gain=gain, peak=peak)
                tag.add(f)

        for key in self.TXXX_MAP:
            try:
                del(tag["TXXX:" + key])
            except KeyError:
                pass
        for key in self.PAM_XXXT:
            if key in self.SDI:
                # we already write it back using non-TXXX frames
                continue
            if key in self:
                value = self[key]
                f = mutagen.id3.TXXX(encoding=encoding_for(value),
                                     text=value.split("\n"),
                                     desc=self.PAM_XXXT[key])
                tag.add(f)

        if (config.getboolean("editing", "save_to_songs") and
                (self.has_rating or self.get("~#playcount", 0) != 0)):
            email = config.get("editing", "save_email").strip()
            email = email or const.EMAIL
            t = mutagen.id3.POPM(email=email,
                                 rating=int(255 * self("~#rating")),
                                 count=self.get("~#playcount", 0))
            tag.add(t)

        with translate_errors():
            audio.save()
        self.sanitize()