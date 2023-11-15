def mt(request):
    return {
        'apertium_api_key': appsettings.MT_APERTIUM_KEY,
        'microsoft_api_key': appsettings.MT_MICROSOFT_KEY,
    }