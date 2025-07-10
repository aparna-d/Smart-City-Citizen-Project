from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, LoginForm, CustomPasswordChangeForm, ProfileUpdateForm, ComplaintForm, TestimonialForm, \
    OfficerAssignForm, ComplaintStatusForm
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout

from .models import Zone, CustomUser, Testimonial, Contact, Complaint, ComplaintAssignment


def home(request):
    testimonials = Testimonial.objects.filter(is_approved=True).order_by('-created_at')[:6]  # Fetch latest 6 approved
    zones = Zone.objects.all()
    return render(request, 'index.html', {'testimonials': testimonials, 'zones': zones})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    form = LoginForm()
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            pwd = form.cleaned_data['password']
            user = authenticate(email=email, password=pwd)
            if user:
                login(request, user)
                messages.success(request, "Login successfully.")
                return redirect('dashboard')
            else:
                error = "Invalid email or password"
    return render(request, 'accounts/login.html', {'form': form, 'error': error})

def dashboard(request):
    if request.user.role == 'admin':
        return render(request, 'admin_dashboard.html')
    elif request.user.role == 'officer':
        return render(request, 'officer_dashboard.html')
    else:
        return render(request, 'citizen_dashboard.html')


def manage_zones(request):
    search_query = request.GET.get('search', '')
    zones_list = Zone.objects.all()


    if search_query:
        zones_list = zones_list.filter(name__icontains=search_query) | zones_list.filter(
            description__icontains=search_query)

    paginator = Paginator(zones_list, 5)
    page_number = request.GET.get('page')
    zones = paginator.get_page(page_number)

    return render(request, 'manage_zones.html', {'zones': zones, 'search_query': search_query})

def add_zone(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            Zone.objects.create(name=name, description=description)
            messages.success(request, 'Zone added successfully!')
        else:
            messages.error(request, 'Zone name is required!')
    return redirect('manage_zones')

def delete_zone(request, zone_id):
    Zone.objects.filter(id=zone_id).delete()
    messages.success(request, 'Zone deleted successfully!')
    return redirect('manage_zones')

def edit_zone(request, id):
    zone = get_object_or_404(Zone, pk=id)
    if request.method == "POST":
        zone.name = request.POST['name']
        zone.description = request.POST['description']
        zone.save()
        messages.success(request, 'Zone updated successfully!')
        return redirect('manage_zones')

def manage_citizens(request):
    search_query = request.GET.get('search', '')
    role_filter = 'citizen'
    citizens = CustomUser.objects.filter(role=role_filter)

    if search_query:
        citizens = citizens.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(aadhaar__icontains=search_query)
        )

    paginator = Paginator(citizens, 10)  # Show 10 citizens per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manage_citizens.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })


def manage_officers(request):
    search_query = request.GET.get('search', '')
    role_filter = 'officer'
    officers = CustomUser.objects.filter(role=role_filter)

    if search_query:
        officers = officers.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(aadhaar__icontains=search_query)
        )

    paginator = Paginator(officers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manage_officers.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })

def delete_officer(request, id):
    CustomUser.objects.filter(id=id).delete()
    messages.success(request, 'Officer deleted successfully!')
    return redirect('manage_officers')

def delete_citizen(request, id):
    CustomUser.objects.filter(id=id).delete()
    messages.success(request, 'Citizen deleted successfully!')
    return redirect('manage_citizens')

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('dashboard')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile_view')
    else:
        form = ProfileUpdateForm(instance=user)
    return render(request, 'profile.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def lodge_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.citizen = request.user
            complaint.save()
            messages.success(request, "Complaint lodged successfully.")
            return redirect('dashboard')
    else:
        form = ComplaintForm()
    return render(request, 'lodge_complaint.html', {'form': form})


def handle_contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        Contact.objects.create(name=name, email=email, message=message)

        messages.success(request, "Thank you for contacting us. We’ll get back to you soon!")
        return redirect('home')
    return redirect('home')

def manage_contacts(request):
    search_query = request.GET.get('search', '')
    contacts = Contact.objects.all().order_by('-submitted_at')

    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(message__icontains=search_query)
        )

    paginator = Paginator(contacts, 10)  # Show 10 contacts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manage_contacts.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })

def delete_contact(request, id):
    Contact.objects.filter(id=id).delete()
    messages.success(request, 'Contact deleted successfully!')
    return redirect('manage_contacts')

def manage_testimonials(request):
    search_query = request.GET.get('search', '')
    testimonials = Testimonial.objects.select_related('user')

    if search_query:
        testimonials = testimonials.filter(user__name__icontains=search_query)

    paginator = Paginator(testimonials.order_by('-created_at'), 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'manage_testimonials.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })

def delete_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, pk=testimonial_id)
    testimonial.delete()
    messages.success(request, "Testimonial deleted successfully.")
    return redirect('manage_testimonials')

def toggle_approval(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, pk=testimonial_id)
    testimonial.is_approved = not testimonial.is_approved
    testimonial.save()
    status = "approved" if testimonial.is_approved else "set to pending"
    messages.success(request, f"Testimonial has been {status}.")
    return redirect('manage_testimonials')

def submit_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user
            testimonial.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('dashboard')  # Adjust redirect as needed
    else:
        form = TestimonialForm()

    return render(request, 'submit_testimonial.html', {'form': form})

def view_complaint_status(request):
    user_complaints = Complaint.objects.filter(citizen=request.user).order_by('-created_at')
    return render(request, 'view_complaint_status.html', {'complaints': user_complaints})

def admin_view_complaints(request):
    query = request.GET.get('q', '')
    complaints = Complaint.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(citizen__name__icontains=query)
    ).order_by('-created_at')

    paginator = Paginator(complaints, 10)
    page = request.GET.get('page')
    complaints = paginator.get_page(page)

    assignments = {a.complaint_id: a.officer for a in ComplaintAssignment.objects.select_related('officer')}

    return render(request, 'admin_complaints_list.html', {
        'complaints': complaints,
        'assignments': assignments,
        'query': query,
    })

def assign_officer(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == 'POST':
        form = OfficerAssignForm(request.POST)
        if form.is_valid():
            officer = form.cleaned_data['officer']
            ComplaintAssignment.objects.create(complaint=complaint, officer=officer)
            complaint.status = 'In Progress'
            complaint.save()
            return redirect('admin_view_complaints')
    else:
        form = OfficerAssignForm()

    return render(request, 'assign_officer.html', {
        'form': form,
        'complaint': complaint
    })

def officer_assigned_complaints(request):
    officer = request.user
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    assignments = ComplaintAssignment.objects.filter(officer=officer)

    complaints = Complaint.objects.filter(
        id__in=assignments.values_list('complaint_id', flat=True)
    )

    if search_query:
        complaints = complaints.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    if status_filter:
        complaints = complaints.filter(status=status_filter)

    paginator = Paginator(complaints.order_by('-created_at'), 5)
    page = request.GET.get('page')
    complaints_page = paginator.get_page(page)

    return render(request, 'officer_assigned_complaints.html', {
        'complaints': complaints_page,
        'search_query': search_query,
        'status_filter': status_filter,
    })

def update_complaint_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == 'POST':
        form = ComplaintStatusForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            return redirect('officer_assigned_complaints')
    else:
        form = ComplaintStatusForm(instance=complaint)

    return render(request, 'update_complaint_status.html', {'form': form, 'complaint': complaint})

def complaint_analytics(request):
    # Count the number of complaints by status
    complaint_status_counts = Complaint.objects.values('status').annotate(count=Count('status'))

    # Count complaints by zone
    complaint_zone_counts = Complaint.objects.values('zone__name').annotate(count=Count('zone'))

    # Monthly complaint counts
    monthly_complaints = Complaint.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')

    context = {
        'complaint_status_counts': complaint_status_counts,
        'complaint_zone_counts': complaint_zone_counts,
        'monthly_complaints': monthly_complaints,
    }
    return render(request, 'complaint_analytics.html', context)

def officer_dashboard_analytics(request):
    # Total complaints
    total_complaints = Complaint.objects.count()

    # Complaints by status
    complaints_by_status = Complaint.objects.values('status').annotate(total=Count('status'))

    # Complaints assigned to officers
    complaints_assigned = ComplaintAssignment.objects.count()

    # Testimonial ratings (average rating)
    avg_rating = Testimonial.objects.aggregate(avg_rating=models.Avg('rating'))['avg_rating']

    # Complaints by Zone
    complaints_by_zone = Complaint.objects.values('zone__name').annotate(total=Count('zone'))

    # Complaints by month (time-based statistics)
    current_month = datetime.now().month
    complaints_by_month = Complaint.objects.filter(created_at__month=current_month).count()

    # Pass the data to the template
    context = {
        'total_complaints': total_complaints,
        'complaints_by_status': complaints_by_status,
        'complaints_assigned': complaints_assigned,
        'avg_rating': avg_rating,
        'complaints_by_zone': complaints_by_zone,
        'complaints_by_month': complaints_by_month,
    }

    return render(request, 'officer_dashboard_analytics.html', context)