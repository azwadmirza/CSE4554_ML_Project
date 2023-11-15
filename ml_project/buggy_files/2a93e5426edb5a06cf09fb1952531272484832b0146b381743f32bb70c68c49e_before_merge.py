def getDrive(drive=None, gauth=None):
    if not drive:
        if not gauth:
            gauth = GoogleAuth(settings_file=os.path.join(config.get_main_dir,'settings.yaml'))
        # Try to load saved client credentials
        gauth.LoadCredentialsFile(os.path.join(config.get_main_dir,'gdrive_credentials'))
        if gauth.access_token_expired:
            # Refresh them if expired
            try:
                gauth.Refresh()
            except RefreshError as e:
                web.app.logger.error("Google Drive error: " + e.message)
            except Exception as e:
                web.app.logger.exception(e)
        else:
            # Initialize the saved creds
            gauth.Authorize()
        # Save the current credentials to a file
        return GoogleDrive(gauth)
    if drive.auth.access_token_expired:
        drive.auth.Refresh()
    return drive