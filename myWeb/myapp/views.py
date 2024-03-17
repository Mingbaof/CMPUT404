from django.shortcuts import render, HttpResponse
from .models import ToDoItem
# Create your views here.
def home(request):
    #print("Hello World1122")
    return render(request, 'home.html')

def todos(request):
    items = ToDoItem.objects.all()
    return render(request, 'todos.html', {"todos": items})