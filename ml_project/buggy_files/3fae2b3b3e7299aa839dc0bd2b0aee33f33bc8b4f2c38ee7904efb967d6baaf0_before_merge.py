    def run_feed(self, feed=None, download=False, ignoreFirst=False, force=False, readout=True):
        """ Run the query for one URI and apply filters """
        self.shutdown = False

        if not feed:
            return "No such feed"

        newlinks = []
        new_downloads = []

        # Preparations, get options
        try:
            feeds = config.get_rss()[feed]
        except KeyError:
            logging.error(T('Incorrect RSS feed description "%s"'), feed)
            logging.info("Traceback: ", exc_info=True)
            return T('Incorrect RSS feed description "%s"') % feed

        uris = feeds.uri()
        defCat = feeds.cat()

        if not notdefault(defCat) or defCat not in sabnzbd.api.list_cats(default=False):
            defCat = None
        defPP = feeds.pp()
        if not notdefault(defPP):
            defPP = None
        defScript = feeds.script()
        if not notdefault(defScript):
            defScript = None
        defPrio = feeds.priority()
        if not notdefault(defPrio):
            defPrio = None

        # Preparations, convert filters to regex's
        regexes = []
        reTypes = []
        reCats = []
        rePPs = []
        rePrios = []
        reScripts = []
        reEnabled = []
        for feed_filter in feeds.filters():
            reCat = feed_filter[0]
            if defCat in ("", "*"):
                reCat = None
            reCats.append(reCat)
            rePPs.append(feed_filter[1])
            reScripts.append(feed_filter[2])
            reTypes.append(feed_filter[3])
            if feed_filter[3] in ("<", ">", "F", "S"):
                regexes.append(feed_filter[4])
            else:
                regexes.append(convert_filter(feed_filter[4]))
            rePrios.append(feed_filter[5])
            reEnabled.append(feed_filter[6] != "0")
        regcount = len(regexes)

        # Set first if this is the very first scan of this URI
        first = (feed not in self.jobs) and ignoreFirst

        # Add SABnzbd's custom User Agent
        feedparser.USER_AGENT = "SABnzbd/%s" % sabnzbd.__version__

        # Read the RSS feed
        msg = ""
        entries = []
        if readout:
            all_entries = []
            for uri in uris:
                msg = ""
                feed_parsed = {}
                uri = uri.replace(" ", "%20").replace("feed://", "http://")
                logging.debug("Running feedparser on %s", uri)
                try:
                    feed_parsed = feedparser.parse(uri)
                except Exception as feedparser_exc:
                    # Feedparser 5 would catch all errors, while 6 just throws them back at us
                    feed_parsed["bozo_exception"] = feedparser_exc
                logging.debug("Finished parsing %s", uri)

                status = feed_parsed.get("status", 999)
                if status in (401, 402, 403):
                    msg = T("Do not have valid authentication for feed %s") % uri
                elif 500 <= status <= 599:
                    msg = T("Server side error (server code %s); could not get %s on %s") % (status, feed, uri)

                entries = feed_parsed.get("entries", [])
                if not entries and "feed" in feed_parsed and "error" in feed_parsed["feed"]:
                    msg = T("Failed to retrieve RSS from %s: %s") % (uri, feed_parsed["feed"]["error"])

                # Exception was thrown
                if "bozo_exception" in feed_parsed and not entries:
                    msg = str(feed_parsed["bozo_exception"])
                    if "CERTIFICATE_VERIFY_FAILED" in msg:
                        msg = T("Server %s uses an untrusted HTTPS certificate") % get_base_url(uri)
                        msg += " - https://sabnzbd.org/certificate-errors"
                    elif "href" in feed_parsed and feed_parsed["href"] != uri and "login" in feed_parsed["href"]:
                        # Redirect to login page!
                        msg = T("Do not have valid authentication for feed %s") % uri
                    else:
                        msg = T("Failed to retrieve RSS from %s: %s") % (uri, msg)

                if msg:
                    # We need to escape any "%20" that could be in the warning due to the URL's
                    logging.warning_helpful(urllib.parse.unquote(msg))
                elif not entries:
                    msg = T("RSS Feed %s was empty") % uri
                    logging.info(msg)
                all_entries.extend(entries)
            entries = all_entries

        # In case of a new feed
        if feed not in self.jobs:
            self.jobs[feed] = {}
        jobs = self.jobs[feed]

        # Error in readout or now new readout
        if readout:
            if not entries:
                return msg
        else:
            entries = jobs

        # Filter out valid new links
        for entry in entries:
            if self.shutdown:
                return

            if readout:
                try:
                    link, infourl, category, size, age, season, episode = _get_link(entry)
                except (AttributeError, IndexError):
                    logging.info(T("Incompatible feed") + " " + uri)
                    logging.info("Traceback: ", exc_info=True)
                    return T("Incompatible feed")
                title = entry.title

                # If there's multiple feeds, remove the duplicates based on title and size
                if len(uris) > 1:
                    skip_job = False
                    for job_link, job in jobs.items():
                        # Allow 5% size deviation because indexers might have small differences for same release
                        if (
                            job.get("title") == title
                            and link != job_link
                            and (job.get("size") * 0.95) < size < (job.get("size") * 1.05)
                        ):
                            logging.info("Ignoring job %s from other feed", title)
                            skip_job = True
                            break
                    if skip_job:
                        continue
            else:
                link = entry
                infourl = jobs[link].get("infourl", "")
                category = jobs[link].get("orgcat", "")
                if category in ("", "*"):
                    category = None
                title = jobs[link].get("title", "")
                size = jobs[link].get("size", 0)
                age = jobs[link].get("age")
                season = jobs[link].get("season", 0)
                episode = jobs[link].get("episode", 0)

            if link:
                # Make sure spaces are quoted in the URL
                link = link.strip().replace(" ", "%20")

                newlinks.append(link)

                if link in jobs:
                    jobstat = jobs[link].get("status", " ")[0]
                else:
                    jobstat = "N"
                if jobstat in "NGB" or (jobstat == "X" and readout):
                    # Match this title against all filters
                    logging.debug("Trying title %s", title)
                    result = False
                    myCat = defCat
                    myPP = defPP
                    myScript = defScript
                    myPrio = defPrio
                    n = 0
                    if ("F" in reTypes or "S" in reTypes) and (not season or not episode):
                        season, episode = sabnzbd.newsunpack.analyse_show(title)[1:3]

                    # Match against all filters until an positive or negative match
                    logging.debug("Size %s", size)
                    for n in range(regcount):
                        if reEnabled[n]:
                            if category and reTypes[n] == "C":
                                found = re.search(regexes[n], category)
                                if not found:
                                    logging.debug("Filter rejected on rule %d", n)
                                    result = False
                                    break
                            elif reTypes[n] == "<" and size and from_units(regexes[n]) < size:
                                # "Size at most" : too large
                                logging.debug("Filter rejected on rule %d", n)
                                result = False
                                break
                            elif reTypes[n] == ">" and size and from_units(regexes[n]) > size:
                                # "Size at least" : too small
                                logging.debug("Filter rejected on rule %d", n)
                                result = False
                                break
                            elif reTypes[n] == "F" and not ep_match(season, episode, regexes[n]):
                                # "Starting from SxxEyy", too early episode
                                logging.debug("Filter requirement match on rule %d", n)
                                result = False
                                break
                            elif (
                                reTypes[n] == "S"
                                and season
                                and episode
                                and ep_match(season, episode, regexes[n], title)
                            ):
                                logging.debug("Filter matched on rule %d", n)
                                result = True
                                break
                            else:
                                if regexes[n]:
                                    found = re.search(regexes[n], title)
                                else:
                                    found = False
                                if reTypes[n] == "M" and not found:
                                    logging.debug("Filter rejected on rule %d", n)
                                    result = False
                                    break
                                if found and reTypes[n] == "A":
                                    logging.debug("Filter matched on rule %d", n)
                                    result = True
                                    break
                                if found and reTypes[n] == "R":
                                    logging.debug("Filter rejected on rule %d", n)
                                    result = False
                                    break

                    if len(reCats):
                        if not result and defCat:
                            # Apply Feed-category on non-matched items
                            myCat = defCat
                        elif result and notdefault(reCats[n]):
                            # Use the matched info
                            myCat = reCats[n]
                        elif category and not defCat:
                            # No result and no Feed-category
                            myCat = cat_convert(category)

                        if myCat:
                            myCat, catPP, catScript, catPrio = cat_to_opts(myCat)
                        else:
                            myCat = catPP = catScript = catPrio = None
                        if notdefault(rePPs[n]):
                            myPP = rePPs[n]
                        elif not (reCats[n] or category):
                            myPP = catPP
                        if notdefault(reScripts[n]):
                            myScript = reScripts[n]
                        elif not (notdefault(reCats[n]) or category):
                            myScript = catScript
                        if rePrios[n] not in (str(DEFAULT_PRIORITY), ""):
                            myPrio = rePrios[n]
                        elif not ((rePrios[n] != str(DEFAULT_PRIORITY)) or category):
                            myPrio = catPrio

                    if cfg.no_dupes() and self.check_duplicate(title):
                        if cfg.no_dupes() == 1:
                            # Dupe-detection: Discard
                            logging.info("Ignoring duplicate job %s", title)
                            continue
                        elif cfg.no_dupes() == 3:
                            # Dupe-detection: Fail
                            # We accept it so the Queue can send it to the History
                            logging.info("Found duplicate job %s", title)
                        else:
                            # Dupe-detection: Pause
                            myPrio = DUP_PRIORITY

                    act = download and not first
                    if link in jobs:
                        act = act and not jobs[link].get("status", "").endswith("*")
                        act = act or force
                        star = first or jobs[link].get("status", "").endswith("*")
                    else:
                        star = first
                    if result:
                        _HandleLink(
                            jobs,
                            link,
                            infourl,
                            title,
                            size,
                            age,
                            season,
                            episode,
                            "G",
                            category,
                            myCat,
                            myPP,
                            myScript,
                            act,
                            star,
                            priority=myPrio,
                            rule=n,
                        )
                        if act:
                            new_downloads.append(title)
                    else:
                        _HandleLink(
                            jobs,
                            link,
                            infourl,
                            title,
                            size,
                            age,
                            season,
                            episode,
                            "B",
                            category,
                            myCat,
                            myPP,
                            myScript,
                            False,
                            star,
                            priority=myPrio,
                            rule=n,
                        )

        # Send email if wanted and not "forced"
        if new_downloads and cfg.email_rss() and not force:
            emailer.rss_mail(feed, new_downloads)

        remove_obsolete(jobs, newlinks)
        return msg