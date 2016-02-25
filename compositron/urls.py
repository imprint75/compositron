from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import home.views

urlpatterns = [
    url(r'^$', home.views.IndexView.as_view(), name='home.index'),
    url(r'^home/?', include('home.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
