from django.conf.urls import url

import home.views

urlpatterns = [
    url(r'^$', home.views.IndexView.as_view(), name='home.index'),
]
