        def tzhandler(default, toconf):
            print("\nPlease choose the correct time zone for your blog. Nikola uses the tz database.")
            print("You can find your time zone here:")
            print("https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
            print("")
            answered = False
            while not answered:
                try:
                    lz = get_localzone()
                except Exception:
                    lz = None
                answer = ask('Time zone', lz if lz else "UTC")
                tz = dateutil.tz.gettz(answer)

                if tz is None:
                    print("    WARNING: Time zone not found.  Searching list of time zones for a match.")
                    all_zones = dateutil.zoneinfo.get_zonefile_instance().zones
                    matching_zones = [zone for zone in all_zones if answer.lower() in zone.lower()]
                    if len(matching_zones) == 1:
                        tz = dateutil.tz.gettz(matching_zones[0])
                        answer = matching_zones[0]
                        print("    Picking '{0}'.".format(answer))
                    elif len(matching_zones) > 1:
                        print("    The following time zones match your query:")
                        print('        ' + '\n        '.join(matching_zones))
                        continue

                if tz is not None:
                    time = datetime.datetime.now(tz).strftime('%H:%M:%S')
                    print("    Current time in {0}: {1}".format(answer, time))
                    answered = ask_yesno("Use this time zone?", True)
                else:
                    print("    ERROR: No matches found.  Please try again.")

            SAMPLE_CONF['TIMEZONE'] = answer