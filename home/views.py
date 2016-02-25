import logging

from django.shortcuts import render
from django.views.generic import View

logger = logging.getLogger(__name__)


class IndexView(View):
    template_name = 'home/index.html'

    def get(self, request, *args, **kwargs):
        logger.debug("hello home view")
        return render(request, self.template_name, locals())
