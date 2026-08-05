"""
User Profile Views
Handles profile display, editing, and password changes
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db.models import Sum

from ..forms import ProfileForm
from ..models import Profile, Order



# PROFILE VIEW - Display user profile information


@login_required(login_url='shop:login')
def profile_view(request):
    """
    Display the user's profile page with:
    - Personal information (name, bio, contact details)
    - Member ID and join date
    - Order statistics (total orders and total spent)
    
    Args:
        request: The HTTP request object
    
    Returns:
        Rendered profile.html template with user and stats context
    """
    
    # Get the currently logged-in user
    user = request.user
    
    # Try to get the user's profile, or create one if it doesn't exist
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        # If profile doesn't exist, create it automatically
        profile = Profile.objects.create(user=user)
    
    # Get all orders for this user
    orders = Order.objects.filter(user=user)
    
    # Count total number of orders
    total_orders = orders.count()
    
    # Calculate total amount spent
    # Sum up the 'total_price' field from all orders
    # If no orders exist, default to 0
    total_spent_data = orders.aggregate(total=Sum('total_price'))
    total_spent = total_spent_data['total'] or 0
    total_spent = round(total_spent, 2)
    
    # Prepare data to send to template
    context = {
        'profile': profile,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'user': user,
    }
    
    # Render and return the profile template
    return render(request, 'shop/profile.html', context)



# EDIT PROFILE VIEW - Allow users to update their profile


@login_required(login_url='shop:login')
def edit_profile_view(request):
    """
    Handle profile editing with form validation and image upload.
    Supports both GET (show form) and POST (save changes) requests.
    
    GET Request:
        - Display the edit profile form pre-filled with current data
    
    POST Request:
        - Validate the submitted form
        - Update user information (first name, last name)
        - Update profile information (bio, phone, address)
        - Handle avatar image upload
        - Show success message and redirect to profile page
    
    Args:
        request: The HTTP request object
    
    Returns:
        GET: Rendered edit_profile.html form
        POST (valid): Redirect to profile page with success message
        POST (invalid): Rendered form with error messages
    """
    
    # Get the currently logged-in user
    user = request.user
    
    # Try to get the user's profile, or create one if it doesn't exist
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        # If profile doesn't exist, create it automatically
        profile = Profile.objects.create(user=user)
    
    # Check if this is a form submission (POST request)
    if request.method == 'POST':
        # Create form with submitted data and files
        form = ProfileForm(request.POST, request.FILES)
        
        # Validate the form
        if form.is_valid():
            # ===== Update User Model Fields =====
            # These fields are part of Django's built-in User model
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()  # Save changes to database
            
            # ===== Update Profile Model Fields =====
            # These fields are part of our custom Profile model
            profile.bio = form.cleaned_data.get('bio', '')
            profile.phone = form.cleaned_data.get('phone', '')
            profile.address = form.cleaned_data.get('address', '')
            profile.banner = form.cleaned_data.get('banner', '')
            
            # ===== Handle Avatar Image Upload =====
            if 'avatar' in request.FILES:
                # User uploaded a new avatar image
                avatar_file = request.FILES['avatar']
                
                # Delete old avatar image if one exists
                if profile.avatar:
                    profile.avatar.delete(save=False)
                
                # Set the new avatar
                profile.avatar = avatar_file
            
            # Save all profile changes to database
            profile.save()
            
            # Show success message to user
            messages.success(
                request, 
                'Your profile has been updated successfully!',
                extra_tags='success'
            )
            
            # Redirect back to profile page to see updated info
            return redirect('shop:profile')
        
        # If form is not valid, it will display errors in the template
        # The form object with errors will be passed to the template automatically
    
    else:
        # This is a GET request (user is viewing the form, not submitting)
        # Pre-fill the form with the user's current information
        
        form = ProfileForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': profile.bio,
            'phone': profile.phone,
            'address': profile.address,
            'avatar': profile.avatar,
            'banner': profile.banner
            # Note: avatar is handled by JavaScript preview, not pre-filled here
        })
    
    # Prepare data to send to template
    context = {
        'form': form,
        'profile': profile,
    }
    
    # Render and return the edit profile template
    return render(request, 'shop/edit_profile.html', context)



# CHANGE PASSWORD VIEW - Allow users to change their password


@login_required(login_url='shop:login')
def change_password_view(request):
    """
    Handle password changes securely using Django's built-in PasswordChangeForm.
    Supports both GET (show form) and POST (change password) requests.
    
    GET Request:
        - Display the password change form (current password + new password fields)
    
    POST Request:
        - Validate the submitted form
        - Check current password is correct
        - Verify new passwords match
        - Update password in database
        - Update session to keep user logged in
        - Show success message
    
    Args:
        request: The HTTP request object
    
    Returns:
        GET: Rendered change_password.html form
        POST (valid): Redirect to profile page with success message
        POST (invalid): Rendered form with error messages
    """
    
    # Get the currently logged-in user
    user = request.user
    
    # Check if this is a form submission (POST request)
    if request.method == 'POST':
        # Create Django's built-in password change form
        # Pass the current user so it can verify old password
        form = PasswordChangeForm(user=user, data=request.POST)
        
        # Validate the form
        if form.is_valid():
            # Save the new password to database
            user = form.save()
            
            # Keep user logged in after password change
            # Without this, user would be logged out
            update_session_auth_hash(request, user)
            
            # Show success message to user
            messages.success(
                request,
                'Your password has been changed successfully!',
                extra_tags='success'
            )
            
            # Redirect back to profile page
            return redirect('shop:profile')
        
        # If form is not valid, errors will display in template
    
    else:
        # This is a GET request (user is viewing the form, not submitting)
        # Create empty password change form
        form = PasswordChangeForm(user=user)
    
    # Prepare data to send to template
    context = {
        'form': form,
    }
    
    # Render and return the change password template
    return render(request, 'shop/change_password.html', context)





