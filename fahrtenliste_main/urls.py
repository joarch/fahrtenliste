from django.conf.urls import url

import views

urlpatterns = [
    url(r'^report_pdf', views.report_pdf)
]
