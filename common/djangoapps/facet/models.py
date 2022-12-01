from django.db import models


# Createed by ywsj.
class Facet(models.Model):
    class Meta:
        db_table = "facet"

    displayname = models.CharField(max_length=100, unique=True)
    number = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=1000)


class Group(models.Model):
    class Meta:
        db_table = "facet_group"

    facet = models.CharField(max_length=100)
    group = models.CharField(max_length=100)


class FacetOfCourse(models.Model):
    class Meta:
        db_table = "facet_group_course"

    facet = models.CharField(max_length=100)
    group = models.CharField(max_length=100)
    course = models.CharField(max_length=100)


class GroupOfLanguage(models.Model):
    class Meta:
        db_table = "facet_group_lang"
        unique_together = ('lang', 'group')

    lang = models.CharField(max_length=100)
    content = models.CharField(max_length=100)
    group = models.ForeignKey(Group, related_name='group_langs', on_delete=models.CASCADE)

    @classmethod
    def get_group(cls, lang, group):
        try:
            return cls.objects.select_related('group').get(lang=lang, group=group).content
        except GroupOfLanguage.DoesNotExist:
            return group.group
