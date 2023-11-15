def make_migrations(base_dir):
    """Create Database Migrations"""
    try:
        python = get_python()
        manage = os.path.join(base_dir, "manage.py")
        args = [python, manage, "makemigrations"]
        subprocess.call(args)
        args = [python, manage, "makemigrations", "StaticAnalyzer"]
        subprocess.call(args)
    except:
        PrintException("[ERROR] Cannot Make Migrations")