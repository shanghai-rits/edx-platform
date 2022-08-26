from django.conf.urls import url
from django.conf import settings
from common.djangoapps.pdf_xblock import views

urlpatterns = [
    url(r'^pdf_xblock/pdf_index/', views.pdf_index, name='pdf_index'),
]
