from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def Create(request):

    print("dedans")
    return render(request , "add_data.html")