from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import datetime

@login_required
def home(request):
    """
    Default home page located at /
    """

    
    current_datetime = datetime.datetime.now()  
    return render(request, "pages/home.html",{"current_datetime":current_datetime})
