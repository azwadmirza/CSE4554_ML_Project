def get_bk_user(request):
    bkuser = None
    if request.weixin_user and not isinstance(request.weixin_user, AnonymousUser):
        try:
            user_property = UserProperty.objects.get(key='wx_userid', value=request.weixin_user.userid)
            bkuser = user_property.user
        except UserProperty.DoesNotExist:
            bkuser = None
    return bkuser or AnonymousUser()