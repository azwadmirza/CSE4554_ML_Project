        def tzhandler(default, toconf):
            print("\nPlease choose the correct time zone for your blog. Nikola uses the tz database.")
            print("You can find your time zone here:")
            print("http://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
            print("")
            answered = False
            while not answered:
                try:
                    lz = get_localzone()
                except:
                    lz = None
                answer = ask('Time zone', lz if lz else "UTC")
                tz = dateutil.tz.gettz(answer)

                if tz is None:
                    print("    WARNING: Time zone not found.  Searching most common timezones for a match.")
                    zonesfile = tarfile.TarFile.open(os.path.join(dateutil.zoneinfo.ZONEINFOFILE))
                    zonenames = [zone for zone in zonesfile.getnames() if answer.lower() in zone.lower()]
                    if len(zonenames) == 1:
                        tz = dateutil.tz.gettz(zonenames[0])
                    elif len(zonenames) > 1:
                        print("    Could not pick one timezone. Choose one of the following:")
                        print('        ' + '\n        '.join(zonenames))
                        continue

                if tz is not None:
                    time = datetime.datetime.now(tz).strftime('%H:%M:%S')
                    print("    Current time in {0}: {1}".format(answer, time))
                    answered = ask_yesno("Use this time zone?", True)
                else:
                    print("    ERROR: Time zone not found.  Please try again.  Time zones are case-sensitive.")

            SAMPLE_CONF['TIMEZONE'] = answer