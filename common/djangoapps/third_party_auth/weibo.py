from social_core.backends.weibo import WeiboOAuth2


class CustomWeiboOAuth2(WeiboOAuth2):
    EXTRA_DATA = [
        ('name', 'user_displayname'),
        ('profile_image_url', 'profile_image_url'),
    ]

    def get_user_details(self, response):
        return {
            'user_displayname': response.get('name', ''),
            'profile_image_url': response.get('profile_image_url', ''),
            'email': 'default@default.com'
        }
