def get_bk_user(request):
    bkuser = None
    if request.weixin_user and not isinstance(request.weixin_user, AnonymousUser):
        user_model = get_user_model()
        try:
            user_property = UserProperty.objects.get(key='wx_userid', value=request.weixin_user.userid)
        except UserProperty.DoesNotExist:
            logger.warning('user[wx_userid=%s] not in UserProperty' % request.weixin_user.userid)
        else:
            bkuser = user_model.objects.get(username=user_property.user.username)
    return bkuser or AnonymousUser()