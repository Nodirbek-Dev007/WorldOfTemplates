from django.shortcuts import render, redirect
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import *
from .tokens import Tokenis
from .decorators import *
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import os
from .models import Product

def Activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and Tokenis.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can now log in.")
        return redirect('Login')
    else:
        messages.error(request, "Activation link is invalid or expired.")
        return redirect('Home')

def Verification(request, user, to_email):
    mail_subject = 'CONFIRM YOUR EMAIL'
    
    message = render_to_string("html/massege.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': Tokenis.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })

    email = EmailMultiAlternatives(
        subject=mail_subject,
        body="Please verify your email by clicking the button below.",
        to=[to_email]
    )
    email.attach_alternative(message, "text/html")
    if email.send():
        messages.success(request, f'Dear {user.username}, We sent a VERIFICATION CODE to your email {to_email}. Please check your inbox.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')

@authenticated
def RegisterPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            if User.objects.filter(email=form.cleaned_data.get('email')).exists():
                messages.error(request, "Email is already in use. Please use a different email.")
            else:
                user = form.save(commit=False)
                user.is_active = False 
                user.save()
                Verification(request, user, form.cleaned_data.get('email'))
                return redirect('Activation')

    context = {'form': form}
    return render(request, 'html/register.html', context)

@authenticated
def ActivationPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        user = User.objects.filter(username=username, email=email).first()

        if user:
            to_email = user.email
            Verification(request, user, to_email)
        else:
            return render(request, 'html/verification.html', {'error': 'User not found'})
    context = {}
    return render(request, 'html/verification.html', context)

@authenticated
def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('Home')
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {}
    return render(request, 'html/login.html', context)

def Logout(request):
    logout(request)
    return redirect('Login')

def Home(request):
    types = Tag.objects.all()
    tag_products = []

    for typ in types:
        products = Product.objects.filter(product_type=typ).order_by('-date_created')[:3]
        for product in products:
            if product.status == 'processed' and product.slide_images:
                pptx_folder = os.path.dirname(product.file.name)
                product.image_preview = f'/media/{pptx_folder}/slide1.jpg'
            else:
                product.image_preview = None
        tag_products.append({'typ': typ, 'products': products})

    context = {'types': types, 'tag_products': tag_products}
    return render(request, 'html/home.html', context)

@login_required(login_url='Login')
def Types(request):
    types = Tag.objects.all()
    products = Product.objects.all()

    for product in products:
        if product.status == 'processed' and product.slide_images:
            pptx_folder = os.path.dirname(product.file.name)
            product.image_preview = f'/media/{pptx_folder}/slide1.jpg'
        else:
            product.image_preview = None

    context = {"types": types, 'products': products}
    return render(request, 'html/types.html', context)

@login_required(login_url='Login')
def ProductType(request, type):
    types = Tag.objects.all()
    product_type = get_object_or_404(Tag, tag_name=type)
    relateds = Product.objects.filter(product_type=product_type)

    for related in relateds:
        if related.status == 'processed' and related.slide_images:
            pptx_folder = os.path.dirname(related.file.name)
            related.image_preview = f'/media/{pptx_folder}/slide1.jpg'
        else:
            related.image_preview = None

    context = {'relateds': relateds, 'types': types}
    return render(request, 'html/ProductType.html', context)

@login_required(login_url='Login')
def searchrelatedProduct(request):
    if request.method == "GET":
        search_term = request.GET.get('search', '')
        relateds = Product.objects.all()
        types = Tag.objects.all()

        if search_term:
            relateds = relateds.filter(product_name__icontains=search_term) | relateds.filter(description__icontains=search_term) | relateds.filter(office_created__icontains=search_term) | relateds.filter(product_type__tag_name__icontains=search_term)
        else:
            relateds = Product.objects.none()

        for related in relateds:
            if related.status == 'processed' and related.slide_images:
                pptx_folder = os.path.dirname(related.file.name)
                related.image_preview = f'/media/{pptx_folder}/slide1.jpg'
            else:
                related.image_preview = None

        context = {'relateds': relateds, 'types': types}
        return render(request, 'html/relatedProduct.html', context)
    else:
        return redirect('/')

@login_required(login_url='Login')
def Products(request, pk):
    product = get_object_or_404(Product, id=pk)
    relateds = Product.objects.filter(product_type__in=product.product_type.all()).exclude(product_name=product)
    types = Tag.objects.all()
    slide_urls = []

    if product.status == 'failed':
        context = {'product': product, 'slide_urls': [], 'relateds': relateds, 'types': types, 'error': product.error_message}
    else:
        if product.status == 'processed' and product.slide_images:
            pptx_folder = os.path.dirname(product.file.name)
            slides_folder = os.path.join(settings.MEDIA_URL, pptx_folder)
            for i in range(1, 4):
                image_path = os.path.join(settings.MEDIA_ROOT, pptx_folder, f"slide{i}.jpg")
                if os.path.exists(image_path):
                    slide_urls.append(f"{slides_folder}/slide{i}.jpg")

        for related in relateds:
            if related.status == 'processed' and related.slide_images:
                pptx_folder = os.path.dirname(related.file.name)
                related.image_preview = f'/media/{pptx_folder}/slide1.jpg'
            else:
                related.image_preview = None

        context = {'product': product, 'slide_urls': slide_urls, 'relateds': relateds, 'types': types}

    return render(request, 'html/product.html', context)

def download_file(request, filename):
    product = get_object_or_404(Product, product_name=filename)
    file_path = product.file.path
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    response['Content-Disposition'] = f'attachment; filename="{product.product_name}.pptx"'
    return response

@login_required(login_url='Login')
def Profile(request):
    customer = request.user.customer
    types = Tag.objects.all()
    form = ProfileInput(instance=customer)

    if request.method == 'POST':
        form = ProfileInput(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    
    context = {'form': form, 'customer': customer, 'types': types}
    return render(request, 'html/profile.html', context)

@login_required(login_url='Login')
def Aboutus(request):
    types = Tag.objects.all()
    context = {'types': types}
    return render(request, 'html/aboutus.html', context)

@login_required(login_url='Login')
def ContactPage(request):
    types = Tag.objects.all()
    context = {'types': types}
    return render(request, 'html/contact.html', context)

def custom_404_handler(request, exception):
    return render(request, 'html/404.html', status=404)