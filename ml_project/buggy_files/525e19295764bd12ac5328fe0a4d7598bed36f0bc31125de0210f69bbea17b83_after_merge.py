def migrate(BASE_DIR):
    """Migrate Database"""
    try:
        python = get_python()
        manage = os.path.join(BASE_DIR, "manage.py")
        args = [python, manage, "migrate"]
        subprocess.call(args)
    except:
        PrintException("Cannot Migrate")