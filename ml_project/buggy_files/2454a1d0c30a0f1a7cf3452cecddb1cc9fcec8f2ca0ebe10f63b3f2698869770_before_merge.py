def add_to_recent_scan(name, md5, url):
    """
    Add Entry to Database under Recent Scan
    """
    try:
        db_obj = RecentScansDB.objects.filter(MD5=md5)
        if not db_obj.exists():
            new_db_obj = RecentScansDB(
                NAME=name, MD5=md5, URL=url, TS=timezone.now())
            new_db_obj.save()
    except:
        PrintException("[ERROR] Adding Scan URL to Database")