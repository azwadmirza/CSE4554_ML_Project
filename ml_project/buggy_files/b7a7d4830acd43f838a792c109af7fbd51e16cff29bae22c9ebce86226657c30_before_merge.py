def jdump(text):
    display.display(json.dumps(text, sort_keys=True, indent=4))