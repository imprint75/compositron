from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'home.views.index', name='home.index'),
]
