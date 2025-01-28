from random import random
# views.py

# Change this line

# to this
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from django.core.mail import send_mail
from django.shortcuts import render, redirect

from django.http import HttpResponseRedirect

from onlineVotingSystem import settings
from .forms import RegistrationForm
from django.contrib import messages

from django.contrib.auth import login, logout, authenticate, update_session_auth_hash

from django.contrib.auth.forms import PasswordChangeForm

from django.contrib.auth.decorators import login_required

from .models import Candidate, ControlVote, Position

from .forms import ChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .validators import validate_complex_password




from .tokens import account_activation_token
def homeView(request):
    return render(request, "poll/home.html")


from .forms import RegistrationForm

# Import necessary modules
from django.core.mail import send_mail
from django.contrib import messages


def activateEmail(request, user, email):
    try:
        # Define email subject and message
        subject = 'Activate Your Account'
        message = f'Dear {user}, please click the following link to activate your account: {request.build_absolute_uri("/login/")}'

        # Send the email
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        # Notify the user
        messages.success(request,
                         f'Activation email sent to {email}. Check your inbox (and spam folder) for further instructions.')
    except Exception as e:
        # Handle any errors that occur during email sending
        messages.error(request, f'Failed to send activation email: {str(e)}')


def registrationView(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            password = cd['password']
            confirm_password = cd['confirm_password']
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return redirect('login')

            # Validate password complexity and date of birth
            try:
                validate_complex_password(password)
            except ValidationError as e:
                messages.error(request, ', '.join(e.messages))
                return redirect('login')
            date_of_birth = cd['date_of_birth']
            # Ensure date of birth is before 2006 (at least 18 years old)
            if date_of_birth.year >= 2006:
                messages.error(request, 'You must be at least 18 years old to register.')
                return redirect('login')
            user = form.save(commit=False)
            user.set_password(password)
            user.save()

            # Generate and save a unique 4-digit voter ID for the user
            voter_id = generate_unique_voter_id()
            VoterID.objects.create(user=user, voter_id=voter_id)

            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('home')
        else:
            # Handle form validation errors
            return render(request, "poll/registration.html", {'form': form})
    else:
        form = RegistrationForm()

    return render(request, "poll/registration.html", {'form': form})
    return render(request, "poll/registration.html", {'form': form, 'note': note})

def generate_unique_voter_id():
    while True:
        voter_id = random.randint(1000, 9999)
        if not VoterID.objects.filter(voter_id=voter_id).exists():
            return voter_id





from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import VoterLoginForm
from .models import VoterID

def loginView(request):
    if request.method == "POST":
        form = VoterLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = VoterLoginForm()

    return render(request, "poll/login.html", {'form': form})



def generate_otp():
    return str(random.randint(100000, 999999))


def my_view(request):
    if request.method == 'POST':
        email = request.POST['email']

        # Generate and send OTP
        otp = generate_otp()
        subject = 'OTP for Verification'
        message = f'Your OTP is: {otp}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list =  [email]
        send_mail(subject, message, email_from, recipient_list)
        # Store OTP in the session
        request.session['otp'] = otp

        return redirect('verify_otp')

    return render(request, 'login.html')



def logoutView(request):
    logout(request)
    return redirect('home')


def dashboardView(request):
    return render(request, "poll/dashboard.html")


def positionView(request):
    obj = Position.objects.all()

    return render(request, "poll/position.html", {'obj': obj})



def candidateView(request, pos):
    obj = get_object_or_404(Position, pk=pos)

    if request.method == "POST":
        temp = ControlVote.objects.get_or_create(user=request.user, position=obj)[0]

        if temp.status == False:
            selected_candidate_id = request.POST.get(obj.title)
            selected_candidate = get_object_or_404(Candidate, pk=selected_candidate_id)
            temp2 = Candidate.objects.get(pk=selected_candidate_id)
            temp2.total_vote += 1
            temp2.save()
            temp.status = True
            temp.save()
            messages.success(request, f'Your vote for {selected_candidate.name} in the position of {obj.title} has been casted successfully.')
            logout(request)  # Logout the user after voting
            return render(request, 'poll/home.html', {'obj': obj})
        else:
            messages.success(request, 'You have already voted for this position.')
            return render(request, 'poll/home.html', {'obj': obj})

    else:
        return render(request, 'poll/candidate.html', {'obj': obj})


def resultView(request):
    obj = Candidate.objects.all().order_by('position', '-total_vote')

    return render(request, "poll/result.html", {'obj': obj})


# The candidateDetailView function is used to render the candidate detail page when the user visits the candidate detail page
def candidateDetailView(request, id):
    # The obj variable is used to store the Candidate object
    obj = get_object_or_404(Candidate, pk=id)

    # The render function is used to render the candidate detail page
    # obj is passed to the candidate detail page to display the details of the candidate
    return render(request, "poll/candidate_detail.html", {'obj': obj})


# The changePasswordView function is used to render the password page when the user visits the password page
@login_required
def changePasswordView(request):
    # if statement is used to check if the request method is POST
    if request.method == "POST":

        # The form variable is used to store the PasswordChangeForm
        form = PasswordChangeForm(user=request.user, data=request.POST)

        # check if the form is valid
        if form.is_valid():
            # User is saved and the session is updated
            form.save()
            update_session_auth_hash(request, form.user)

            # The user is redirected to the dashboard page
            return redirect('dashboard')
    else:

        # if the request method is not POST then the render function is used to render the password page
        form = PasswordChangeForm(user=request.user)

    # The render function is used to render the password page
    return render(request, "poll/password.html", {'form': form})


# The editProfileView function is used to render the edit profile page when the user visits the edit profile page
def editProfileView(request):

    if request.method == "POST":

        form = ChangeForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:

        form = ChangeForm(instance=request.user)

    return render(request, "poll/edit_profile.html", {'form': form})

import random

def generate_unique_voter_id():
    while True:
        voter_id = random.randint(1000, 9999)
        if not VoterID.objects.filter(voter_id=voter_id).exists():
            return voter_id





