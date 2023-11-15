def authenticate_google_drive():
    authUrl = gdriveutils.Gauth.Instance().auth.GetAuthUrl()
    return redirect(authUrl)