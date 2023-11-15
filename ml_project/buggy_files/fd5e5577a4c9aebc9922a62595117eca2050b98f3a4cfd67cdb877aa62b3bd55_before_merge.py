def get_json(url, desc):
    r = requests.get(url)
    if r.status_code != 200:
        prints("Couldn't fetch %s. Please find a model for your spaCy installation "
               "(v%s), and download it manually." % (desc, about.__version__),
               about.__docs__, title="Server error (%d)" % r.status_code, exits=True)
    return r.json()