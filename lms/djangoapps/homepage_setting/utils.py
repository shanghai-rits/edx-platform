from .models import BannerSetting


def init_banner_setting():
    if BannerSetting.objects.filter(name='video').count() < 1:
        BannerSetting.objects.create(name='video')

    if BannerSetting.objects.filter(name='image').count() < 1:
        BannerSetting.objects.create(name='image')


def get_homepage_setting(name=None):
    return BannerSetting.objects.filter(name=name)[0]


def get_setting_url(name=None):
    init_banner_setting()
    return get_homepage_setting(name).url_path
