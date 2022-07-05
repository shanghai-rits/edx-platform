from social_core.backends.weixin import WeixinOAuth2
import social_django

class CustomWeixinOAuth2(WeixinOAuth2):
    ID_KEY = 'unionid'

    EXTRA_DATA = [
        ('nickname', 'user_displayname'),
        ('headimgurl', 'profile_image_url'),
    ]

    def get_user_details(self, response):
        return {
            'user_displayname': response.get('nickname', ''),
            'profile_image_url': response.get('headimgurl', ''),
            'email': 'default@default.com'
        }

    def do_auth(self, access_token, *args, **kwargs):
        if kwargs.get('response', None) is not None:
            openid = kwargs['response']['openid']
            unionid = kwargs['response']['unionid']

            social_django.models.UserSocialAuth.objects.filter(uid=openid, provider='weixin').update(uid=unionid)
        return super(CustomWeixinOAuth2, self).do_auth(access_token, *args, **kwargs)
