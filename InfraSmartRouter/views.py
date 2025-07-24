
from django.shortcuts import render

from accounts.models import Container

def index(request):
    return render(request, "index.html")    

def container_list(request):
    containers = Container.objects.all()
    context = {
        'containers': containers,
    }
    
    # Return partial template for HTMX requests
    if request.headers.get('HX-Request'):
        return render(request, "container_partial.html", context)
    
    return render(request, "container_list.html", context)

