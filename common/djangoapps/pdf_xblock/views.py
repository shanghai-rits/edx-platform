from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.http import HttpResponseRedirect
from django.http import FileResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.djangoapps.edxmako.shortcuts import render_to_response

import urllib.request, urllib.error, urllib.parse

@login_required
def pdf_index(request):
    template = 'pdf_xblock_viewer.html'
    current_url = request.GET.get('file')
    return render_to_response(template, {'current_url': current_url})
