def authenticate_google_drive():
    try:
        authUrl = gdriveutils.Gauth.Instance().auth.GetAuthUrl()
    except gdriveutils.InvalidConfigError:
        flash(_(u'Google Drive setup not completed, try to deactivate and activate Google Drive again'),
              category="error")
        return redirect(url_for('index'))
    return redirect(authUrl)