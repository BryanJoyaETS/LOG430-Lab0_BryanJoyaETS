from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

# API REST : POST /api/clients/
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Formulaire HTML : GET/POST /register/
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
