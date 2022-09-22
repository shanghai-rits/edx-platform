from django.db import models

# Created by ywsj.
class RecommendedCourses(models.Model):
    class Meta:
        db_table = "recommended_courses"
    unicodecoursekey = models.CharField(max_length=100, primary_key=True)

