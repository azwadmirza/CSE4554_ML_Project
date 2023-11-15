def read_feeds(bot, force=False):
    if not bot.memory['rss_manager'].running and not force:
        return

    sub = bot.db.substitution
    conn = bot.db.connect()
    c = conn.cursor()
    c.execute('SELECT * FROM rss_feeds')
    feeds = c.fetchall()
    if not feeds:
        bot.debug(__file__, "No RSS feeds to check.", 'warning')
        return

    for feed_row in feeds:
        feed = RSSFeed(feed_row)
        if not feed.enabled:
            continue

        def disable_feed():
            c.execute('''
                UPDATE rss_feeds SET enabled = {0}
                WHERE channel = {0} AND feed_name = {0}
                '''.format(sub), (0, feed.channel, feed.name))
            conn.commit()

        try:
            fp = feedparser.parse(feed.url, etag=feed.etag, modified=feed.modified)
        except IOError as e:
            bot.debug(__file__, "Can't parse feed on {0}, disabling ({1})".format(
                feed.name, str(e)), 'warning')
            disable_feed()
            continue

        # fp.status will only exist if pulling from an online feed
        status = getattr(fp, 'status', None)

        bot.debug(feed.channel, "{0}: status = {1}, version = '{2}', items = {3}".format(
            feed.name, status, fp.version, len(fp.entries)), 'verbose')

        # check for malformed XML
        if fp.bozo:
            bot.debug(__file__, "Got malformed feed on {0}, disabling ({1})".format(
                feed.name, fp.bozo_exception.getMessage()), 'warning')
            disable_feed()
            continue

        # check HTTP status
        if status == 301:  # MOVED_PERMANENTLY
            bot.debug(
                __file__,
                "Got HTTP 301 (Moved Permanently) on {0}, updating URI to {1}".format(
                feed.name, fp.href), 'warning')
            c.execute('''
                UPDATE rss_feeds SET feed_url = {0}
                WHERE channel = {0} AND feed_name = {0}
                '''.format(sub), (fp.href, feed.channel, feed.name))
            conn.commit()

        elif status == 410:  # GONE
            bot.debug(__file__, "Got HTTP 410 (Gone) on {0}, disabling".format(
                feed.name), 'warning')
            disable_feed()

        if not fp.entries:
            continue

        feed_etag = getattr(fp, 'etag', None)
        feed_modified = getattr(fp, 'modified', None)

        entry = fp.entries[0]
        # parse published and updated times into datetime objects (or None)
        entry_dt = (datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    if hasattr(entry, 'published_parsed') else None)
        entry_update_dt = (datetime.fromtimestamp(time.mktime(entry.updated_parsed))
                           if hasattr(entry, 'updated_parsed') else None)

        # check if article is new, and skip otherwise
        if (feed.title == entry.title and feed.link == entry.link
                and feed.etag == feed_etag and feed.modified == feed_modified):
            bot.debug(__file__, u"Skipping previously read entry: [{0}] {1}".format(
                feed.name, entry.title), 'verbose')
            continue

        # save article title, url, and modified date
        c.execute('''
            UPDATE rss_feeds
            SET article_title = {0}, article_url = {0}, published = {0}, etag = {0}, modified = {0}
            WHERE channel = {0} AND feed_name = {0}
            '''.format(sub), (entry.title, entry.link, entry_dt, feed_etag, feed_modified,
                              feed.channel, feed.name))
        conn.commit()

        if feed.published and entry_dt:
            published_dt = datetime.strptime(feed.published, "%Y-%m-%d %H:%M:%S")
            if published_dt >= entry_dt:
                # This will make more sense once iterating over the feed is
                # implemented. Once that happens, deleting or modifying the
                # latest item would result in the whole feed getting re-msg'd.
                # This will prevent that from happening.
                bot.debug(__file__, u"Skipping older entry: [{0}] {1}, because {2} >= {3}".format(
                    feed.name, entry.title, published_dt, entry_dt), 'verbose')
                continue

        # create message for new entry
        message = u"[\x02{0}\x02] \x02{1}\x02 {2}".format(
            colour_text(feed.name, feed.fg, feed.bg), entry.title, entry.link)

        # append update time if it exists, or published time if it doesn't
        timestamp = entry_update_dt or entry_dt
        if timestamp:
            # attempt to get time format from preferences
            tformat = ''
            if feed.channel in bot.db.preferences:
                tformat = bot.db.preferences.get(feed.channel, 'time_format') or tformat
            if not tformat and bot.config.has_option('clock', 'time_format'):
                tformat = bot.config.clock.time_format

            message += " - {0}".format(timestamp.strftime(tformat or '%F - %T%Z'))

        # print message
        bot.msg(feed.channel, message)

    conn.close()