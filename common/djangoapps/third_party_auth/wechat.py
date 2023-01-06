from social_core.backends.weixin import WeixinOAuth2
import social_django

class CustomWeixinOAuth2(WeixinOAuth2):
    ID_KEY = 'unionid'

    EXTRA_DATA = [
        ('nickname', 'user_displayname'),
        ('headimgurl', 'profile_image_url'),
    ]

    def get_user_details(self, response):
        nickname = response.get('nickname', '').encode("raw_unicode_escape").decode("utf-8")

        return {
            'user_displayname': nickname,
            'profile_image_url': response.get('headimgurl', ''),
            'email': 'default@example.com'
        }

    def do_auth(self, access_token, *args, **kwargs):
        if kwargs.get('response', None) is not None:
            openid = kwargs['response']['openid']
            unionid = kwargs['response']['unionid']

            social_django.models.UserSocialAuth.objects.filter(uid=openid, provider='weixin').update(uid=unionid)
        
        if kwargs.get('user', None) is not None:
            kwargs['response'] = {}
            kwargs['response']['openid'] = self.data.get('openid')
            kwargs['response']['unionid'] = self.data.get('unionid')
        
        return super(CustomWeixinOAuth2, self).do_auth(access_token, *args, **kwargs)
