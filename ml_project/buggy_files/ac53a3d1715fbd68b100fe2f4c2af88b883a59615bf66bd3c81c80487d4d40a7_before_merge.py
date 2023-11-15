def PrintException(msg, web=False):
    try:
        LOGPATH = settings.LOG_DIR
    except:
        LOGPATH = os.path.join(settings.BASE_DIR, "logs/")
    if not os.path.exists(LOGPATH):
        os.makedirs(LOGPATH)
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    dat = '\n[' + st + ']\n' + msg + \
        ' ({0}, LINE {1} "{2}"): {3}'.format(
            filename, lineno, line.strip(), exc_obj)
    if platform.system() == "Windows":
        logger.error(dat)
    else:
        if web:
            logger.error(Color.BOLD + Color.ORANGE + dat + Color.END)
        else:
            logger.error(Color.BOLD + Color.RED + dat + Color.END)
    with open(LOGPATH + 'MobSF.log', 'a') as f:
        f.write(dat)