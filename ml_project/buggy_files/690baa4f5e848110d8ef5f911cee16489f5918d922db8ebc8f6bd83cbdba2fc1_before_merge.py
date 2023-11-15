def kali_fix(BASE_DIR):
    try:
        if platform.system() == "Linux" and platform.dist()[0] == "Kali":
            fix_path = os.path.join(BASE_DIR, "scripts/kali_fix.sh")
            subprocess.call(["chmod", "a+x", fix_path])
            subprocess.call([fix_path], shell=True)
    except:
        PrintException("[ERROR] Cannot run Kali Fix")