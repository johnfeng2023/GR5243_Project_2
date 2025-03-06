from django.shortcuts import render

def home(request):
    return render(request, "dataset_app/index.html")

