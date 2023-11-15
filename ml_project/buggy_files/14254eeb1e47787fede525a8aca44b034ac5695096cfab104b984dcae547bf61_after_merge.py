    def __call__(self, key, default=u"", connector=" - ", joiner=', '):
        """Return the value(s) for a key, synthesizing if necessary.
        Multiple values for a key are delimited by newlines.

        A default value may be given (like `dict.get`);
        the default default is an empty unicode string
        (even if the tag is numeric).

        If a tied tag ('a~b') is requested, the `connector` keyword
        argument may be used to specify what it is tied with.
        In case the tied tag contains numeric and file path tags, the result
        will still be a unicode string.
        The `joiner` keyword specifies how multiple *values* will be joined
        within that tied tag output, e.g.
            ~people~title = "Kanye West, Jay Z - New Day"

        For details on tied tags, see the documentation for `util.tagsplit`.
        """

        if key[:1] == "~":
            key = key[1:]
            if "~" in key:
                real_key = "~" + key
                values = []
                sub_tags = util.tagsplit(real_key)
                # If it's genuinely a tied tag (not ~~people etc), we want
                # to delimit the multi-values separately from the tying
                j = joiner if len(sub_tags) > 1 else "\n"
                for t in sub_tags:
                    vs = [decode_value(real_key, v) for v in (self.list(t))]
                    v = j.join(vs)
                    if v:
                        values.append(v)
                return connector.join(values) or default
            elif key == "#track":
                try:
                    return int(self["tracknumber"].split("/")[0])
                except (ValueError, TypeError, KeyError):
                    return default
            elif key == "#disc":
                try:
                    return int(self["discnumber"].split("/")[0])
                except (ValueError, TypeError, KeyError):
                    return default
            elif key == "length":
                length = self.get("~#length")
                if length is None:
                    return default
                else:
                    return util.format_time_display(length)
            elif key == "#rating":
                return dict.get(self, "~" + key, config.RATINGS.default)
            elif key == "rating":
                return util.format_rating(self("~#rating"))
            elif key == "people":
                return "\n".join(self.list_unique(PEOPLE)) or default
            elif key == "people:real":
                # Issue 1034: Allow removal of V.A. if others exist.
                unique = self.list_unique(PEOPLE)
                # Order is important, for (unlikely case): multiple removals
                for val in VARIOUS_ARTISTS_VALUES:
                    if len(unique) > 1 and val in unique:
                        unique.remove(val)
                return "\n".join(unique) or default
            elif key == "people:roles":
                return (self._role_call("performer", PEOPLE)
                        or default)
            elif key == "peoplesort":
                return ("\n".join(self.list_unique(PEOPLE_SORT)) or
                        self("~people", default, connector))
            elif key == "peoplesort:roles":
                # Ignores non-sort tags if there are any sort tags (e.g. just
                # returns "B" for {artist=A, performersort=B}).
                # TODO: figure out the "correct" behavior for mixed sort tags
                return (self._role_call("performersort", PEOPLE_SORT)
                        or self("~peoplesort", default, connector))
            elif key in ("performers", "performer"):
                return self._prefixvalue("performer") or default
            elif key in ("performerssort", "performersort"):
                return (self._prefixvalue("performersort") or
                        self("~" + key[-4:], default, connector))
            elif key in ("performers:roles", "performer:roles"):
                return (self._role_call("performer") or default)
            elif key in ("performerssort:roles", "performersort:roles"):
                return (self._role_call("performersort")
                        or self("~" + key.replace("sort", ""), default,
                                connector))
            elif key == "basename":
                return os.path.basename(self["~filename"]) or self["~filename"]
            elif key == "dirname":
                return os.path.dirname(self["~filename"]) or self["~filename"]
            elif key == "uri":
                try:
                    return self["~uri"]
                except KeyError:
                    return fsn2uri(self["~filename"])
            elif key == "format":
                return self.get("~format", str(self.format))
            elif key == "codec":
                codec = self.get("~codec")
                if codec is None:
                    return self("~format")
                return codec
            elif key == "encoding":
                parts = filter(None,
                               [self.get("~encoding"), self.get("encodedby")])
                encoding = u"\n".join(parts)
                return encoding or default
            elif key == "language":
                codes = self.list("language")
                if not codes:
                    return default
                return u"\n".join(iso639.translate(c) or c for c in codes)
            elif key == "bitrate":
                return util.format_bitrate(self("~#bitrate"))
            elif key == "#date":
                date = self.get("date")
                if date is None:
                    return default
                return util.date_key(date)
            elif key == "year":
                return self.get("date", default)[:4]
            elif key == "#year":
                try:
                    return int(self.get("date", default)[:4])
                except (ValueError, TypeError, KeyError):
                    return default
            elif key == "originalyear":
                return self.get("originaldate", default)[:4]
            elif key == "#originalyear":
                try:
                    return int(self.get("originaldate", default)[:4])
                except (ValueError, TypeError, KeyError):
                    return default
            elif key == "#tracks":
                try:
                    return int(self["tracknumber"].split("/")[1])
                except (ValueError, IndexError, TypeError, KeyError):
                    return default
            elif key == "#discs":
                try:
                    return int(self["discnumber"].split("/")[1])
                except (ValueError, IndexError, TypeError, KeyError):
                    return default
            elif key == "lyrics":
                # First, try the embedded lyrics.
                try:
                    return self["lyrics"]
                except KeyError:
                    pass

                try:
                    return self["unsyncedlyrics"]
                except KeyError:
                    pass

                # If there are no embedded lyrics, try to read them from
                # the external file.
                try:
                    with open(self.lyric_filename, "rb") as fileobj:
                        print_d("Reading lyrics from %s" % self.lyric_filename)
                        text = fileobj.read().decode("utf-8", "replace")
                        # try to skip binary files
                        if "\0" in text:
                            return default
                        return text
                except EnvironmentError:
                    return default
            elif key == "filesize":
                return util.format_size(self("~#filesize", 0))
            elif key == "playlists":
                # See Issue 876
                # Avoid circular references from formats/__init__.py
                from quodlibet.util.collection import Playlist
                playlists = Playlist.playlists_featuring(self)
                return "\n".join([s.name for s in playlists]) or default
            elif key.startswith("#replaygain_"):
                try:
                    val = self.get(key[1:], default)
                    return round(float(val.split(" ")[0]), 2)
                except (ValueError, TypeError, AttributeError):
                    return default
            elif key[:1] == "#":
                key = "~" + key
                if key in self:
                    return self[key]
                elif key in NUMERIC_ZERO_DEFAULT:
                    return 0
                else:
                    try:
                        val = self[key[2:]]
                    except KeyError:
                        return default
                    try:
                        return int(val)
                    except ValueError:
                        try:
                            return float(val)
                        except ValueError:
                            return default
            else:
                return dict.get(self, "~" + key, default)

        elif key == "title":
            title = dict.get(self, "title")
            if title is None:
                basename = self("~basename")
                return "%s [%s]" % (
                    decode_value("~basename", basename), _("Unknown"))
            else:
                return title
        elif key in SORT_TO_TAG:
            try:
                return self[key]
            except KeyError:
                key = SORT_TO_TAG[key]
        return dict.get(self, key, default)