from social_core.backends.qq import QQOAuth2


class CustomQQOAuth2(QQOAuth2):
    EXTRA_DATA = [
        ('nickname', 'user_displayname'),
        ('figureurl_qq_1', 'profile_image_url'),
    ]

    def get_user_details(self, response):
        return {
            'user_displayname': response.get('nickname', ''),
            'profile_image_url': response.get('figureurl_qq_1', ''),
            'email': 'default@default.com'
        }
