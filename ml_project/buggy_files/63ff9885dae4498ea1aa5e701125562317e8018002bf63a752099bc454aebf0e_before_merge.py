def render_title_template(*args, **kwargs):
    return render_template(instance=config.config_calibre_web_title, *args, **kwargs)