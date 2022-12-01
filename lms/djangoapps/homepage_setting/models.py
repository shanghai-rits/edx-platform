from django.db import models


# Create your models here.
class BannerSetting(models.Model):
    name = models.TextField(blank=True, default="")
    url_path = models.TextField(blank=True, default="")

    class Meta:
        db_table = "homepage_banner_setting"
