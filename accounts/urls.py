from django.urls import path
from .views import register_view, login_view, dashboard, add_zone, delete_zone, manage_zones, edit_zone, \
    manage_citizens, manage_officers, delete_citizen, delete_officer, change_password_view, profile_view, \
    lodge_complaint, home, handle_contact, manage_contacts, delete_contact, manage_testimonials, delete_testimonial, \
    toggle_approval, submit_testimonial, view_complaint_status, admin_view_complaints, assign_officer, \
    officer_assigned_complaints, update_complaint_status, complaint_analytics, officer_dashboard_analytics

urlpatterns = [
    path('', home, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('dashboard', dashboard, name='dashboard'),
    path('edit_zone/<int:id>/', edit_zone, name='edit_zone'),
    path('manage_zones/', manage_zones, name='manage_zones'),
    path('delete_zone/<int:zone_id>/', delete_zone, name='delete_zone'),
    path('add_zone/', add_zone, name='add_zone'),
    path('manage_citizens/', manage_citizens, name='manage_citizens'),
    path('manage_contacts/', manage_contacts, name='manage_contacts'),
    path('manage_officers/', manage_officers, name='manage_officers'),
    path('delete_officer/<int:id>/', delete_officer, name='delete_officer'),
    path('delete_citizen/<int:id>/', delete_citizen, name='delete_citizen'),
    path('delete_contact/<int:id>/', delete_contact, name='delete_contact'),
    path('change_password_view/', change_password_view, name='change_password_view'),
    path('profile_view/', profile_view, name='profile_view'),
    path('logout_view/', login_view, name='logout_view'),
    path('lodge_complaint/', lodge_complaint, name='lodge_complaint'),
    path('handel_contact/', handle_contact, name='handle_contact'),
    path('manage_testimonials/', manage_testimonials, name='manage_testimonials'),
    path('delete_testimonial/<int:testimonial_id>/', delete_testimonial, name='delete_testimonial'),
    path('toggle_approval/<int:testimonial_id>/', toggle_approval, name='toggle_approval'),
    path('submit_testimonial/', submit_testimonial, name='submit_testimonial'),
    path('view_complaint_status/', view_complaint_status, name='view_complaint_status'),
    path('admin_view_complaints/', admin_view_complaints, name='admin_view_complaints'),
    path('assign_officer/<int:complaint_id>/', assign_officer, name='assign_officer'),
    path('officer_assigned_complaints/', officer_assigned_complaints, name='officer_assigned_complaints'),
    path('update_complaint_status/<int:complaint_id>/', update_complaint_status, name='update_complaint_status'),
    path('complaint_analytics/', complaint_analytics, name='complaint_analytics'),
    path('officer_dashboard_analytics', officer_dashboard_analytics, name='officer_dashboard_analytics'),
]
