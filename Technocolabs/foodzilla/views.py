from django.shortcuts import render,redirect
#from django.contrib.auth.forms import UserCreationForm
#from .forms import CreateUserForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.models import User
from django.views.generic import View 
from email_validator import validate_email
from .utils import cartData
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import json
from .models import *





# Create your views here.
class HomeViwe(View):
    def get(self, request):
        return render(request, 'index.html')

class CheckoutView(View):
    def get(self,request):
        data = cartData(request)
        return render(request, 'checkout.html')

    def post(request):
	    data = cartData(request)
	
	    cartItems = data['cartItems']
	    order = data['order']
	    items = data['items']

	    context = {'items':items, 'order':order, 'cartItems':cartItems}
	    return render(request, 'checkout.html', context)

class CartView(View):
    def get(self,request):
        data = cartData(request)
        return render(request, 'cart.html')

    def post(self,request):
        data = cartData(request)

        cartItems = data['cartItems']
        order = data['order']
        items = data['items']
        context ={'items':items, 'order':order, 'cartItems':cartItems}
        return render(request, 'cart.html', context)



class UpdateItemView(View):
    def update_Item(request):
	    data = json.loads(request.body)
	    productId = data['productId']
	    action = data['action']
	    print('Action:', action)
	    print('Product:', productId)
  
	    customer = request.user.customer
	    product = Product.objects.get(id=productId)
	    order, created = Order.objects.get_or_create(customer=customer, complete=False)

	    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	    if action == 'add':
		    orderItem.quantity = (orderItem.quantity + 1)
	    elif action == 'remove':
		    orderItem.quantity = (orderItem.quantity - 1)

	    orderItem.save()

	    if orderItem.quantity <= 0:
		    orderItem.delete()

	    return JsonResponse('Item was added', safe=False)

class AccountsView(View):
    def get(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username,password=password)
        if not user:
            return redirect('register')
        return redirect('login')

class RegistrationView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        context = {
            'data': request.POST,
            'has_error': False

        }

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if len(password) < 6 :
            messages.add_message(request,messages.ERROR,
                                 'password should be atleast 6 character long')
            context['has_error'] = True
        if password != password2:
            messages.add_message(request, messages.ERROR,
                                 "password don't match")
            context['has_error'] = True
        
        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'please provide a valid email')
            context['has_error'] = True

        try:
            if User.objects.get(email=email):
                messages.add_message(request, messages.ERROR,
                                     'Email is taken')
                context['has_error'] = True

        except Exception as identifier:
            pass

        try:
            if User.objects.get(username=username):
                messages.add_message(
                    request, messages.ERROR, 'Username is taken')
                context['has_error'] = True
        except Exception as identifier:
            pass

        if context['has_error']:
            return render(request, 'register.html', context, status=400)

        user = User.objects.create_user(username=username,email=email)
        user.set_password(password)
        user.is_active = False
        user.save()

        return redirect('login')

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        context = {
            'data': request.POST,
            'has_error': False
        }

        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == '':
            messages.add_message(
                request, messages.ERROR,
                'Username is required'
            )
            context['has_error'] = True

        if password == '':
            messages.add_message(
                request, messages.ERROR,
                'Password is required'
            )
            context['has_error'] = True

        user = authenticate(
            request, username=username, password=password
        )

        if not user and not context['has_error']:
            messages.add_message(
                request, messages.ERROR,
                'Invalid login'
            )
            context['has_error'] = True

        if context['has_error']:
            return render(
                request, 'login.html', status=401, context=context
            )
        login(request,user)
        return redirect('home')

    
class logoutView(View):
    def post(self, request):
        logout(request)
        messages.add_message(request,messages.SUCCESS, 'Logout successfully')
        return redirect('login')





    


