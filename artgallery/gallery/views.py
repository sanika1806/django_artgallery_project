import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from decimal import Decimal
from .models import ArtPiece

from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, ArtPiece
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect
from django.core.mail import send_mail



from django.contrib import messages

from django.contrib.auth.models import User





from django.contrib.auth import logout


from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate

from .forms import RegisterForm
from django.contrib.auth import logout



razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))







# View for the homepage
def home(request):
    return render(request, 'gallery/home.html')

# View for the gallery page with Add to Cart functionality
def gallery(request):
    # Get the search query from GET parameters (if any)
    query = request.GET.get('query', '').strip()  # default to empty string if no query

    # If there's a search query, filter art pieces based on the title (or other fields)
    if query:
        art_pieces = ArtPiece.objects.filter(title__icontains=query)
    else:
        art_pieces = ArtPiece.objects.all()

    # Handle 'Add to Cart' functionality (POST request)
    if request.method == 'POST':
        art_piece_id = request.POST.get('art_piece_id')
        try:
            art_piece = ArtPiece.objects.get(id=art_piece_id)
        except ArtPiece.DoesNotExist:
            art_piece = None

        if art_piece:
            # Initialize the cart if it doesn't exist in the session
            cart = request.session.get('cart', [])

            # Add the art piece to the cart
            cart.append({
                'id': art_piece.id,
                'title': art_piece.title,
                'price': float(art_piece.price),  # Convert Decimal to float
                'image': art_piece.image.url,
                'artist_name': art_piece.artist_name,
            })
            request.session['cart'] = cart

            # Display success message
            request.session['message'] = f"{art_piece.title} has been added to your cart."
            return redirect('gallery')  # Redirect back to the gallery page

    # Check for success message in session
    message = request.session.pop('message', None)

    # Render the gallery page with the filtered or all art pieces and the search query
    return render(request, 'gallery/gallery.html', {
        'art_pieces': art_pieces,
        'message': message,
        'query': query  # Pass the search query back to the template
    })
# View for the cart page
def cart(request):
    # Retrieve the cart from the session
    cart = request.session.get('cart', [])
    total_price = sum(Decimal(item['price']) for item in cart)  # Convert back to Decimal for accuracy

    # Handle removing an item from the cart
    if request.method == 'POST':
        item_id_to_remove = request.POST.get('remove_item_id')
        cart = [item for item in cart if str(item['id']) != item_id_to_remove]
        request.session['cart'] = cart
        request.session['message'] = "Item removed from cart."
        return redirect('cart')  # Redirect back to the cart page

    # Check for success message in session
    message = request.session.pop('message', None)

    return render(request, 'gallery/cart.html', {
        'cart': cart,
        'total_price': float(total_price),  # Ensure total is JSON serializable
        'message': message,
    })

# View for the about page
def about(request):
    return render(request, 'gallery/about.html')














@login_required
def checkout(request):
    cart = request.session.get('cart', [])
    if not cart:
        return redirect('cart')

    if request.method == 'POST':
        # Calculate the total price
        total_price = sum(Decimal(item['price']) for item in cart)
        
        # Create the order (status will be 'Unpaid' by default)
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            is_paid=False,  # Initial status is 'Unpaid'
        )

        # Add items to the OrderItem model
        for item in cart:
            ArtPiece.objects.get(id=item['id'])  # Get the corresponding ArtPiece
            OrderItem.objects.create(
                order=order,
                art_piece=ArtPiece.objects.get(id=item['id']),
                quantity=1,  # Adjust if needed
            )

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': int(total_price * 100),  # Convert to paisa
            'currency': 'INR',
            'payment_capture': 1,
        })

        # Pass the order and razorpay details to the template
        return render(request, 'gallery/payment.html', {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'total_price': total_price,
            'order_id': order.id,
        })
    
    return render(request, 'gallery/checkout.html', {'cart': cart})



@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'gallery/order_history.html', {'orders': orders})

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Fetch the order by its ID
        order = Order.objects.get(id=data['order_id'])
        
        # Verify payment success (you can add more validation here)
        order.is_paid = True
        order.save()

        # You can also send a confirmation email or SMS here
        send_mail(
            'Payment Successful',
            f"Your payment for Order #{order.id} has been successfully processed.",
            settings.EMAIL_HOST_USER,
            [order.user.email],  # Send email to the customer
            fail_silently=False,
        )

        # Return success status
        return JsonResponse({'status': 'success'})


def create_payment(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({'amount': 50000, 'currency': 'INR', 'payment_capture': '1'})
    return render(request, 'payment.html', {'payment': payment})



def contact(request):
    if request.method == 'POST':
        # Get data from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # You can handle this data as you like (save it to the database, etc.)
        # For example, sending an email to the gallery owner:
        send_mail(
            'New Contact Form Submission',
            f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage:\n{message}",
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],  # Send the email to the admin's email address
            fail_silently=False,
        )

        # Set a success message
        message = "Thank you for reaching out to us! We will get back to you shortly."
        return render(request, 'gallery/contact.html', {'message': message})

    return render(request, 'gallery/contact.html')



# Registration view
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Save the user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Set the password properly
            user.save()
            
            # Automatically log the user in
            login(request, user)
            
            return redirect('home')  # Redirect to the homepage after successful registration
    else:
        form = RegisterForm()

    return render(request, 'gallery/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate the user and log them in
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to homepage after login
    else:
        form = AuthenticationForm()

    return render(request, 'gallery/login.html', {'form': form})



# Logout view
def logout_view(request):
    logout(request)  # Log out the user
    return redirect('home')  # Redirect to homepage after logout

