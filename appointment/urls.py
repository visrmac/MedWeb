from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "appointment"

urlpatterns = [
    path("appointments/p/", views.AppointmentsForAPatientView.as_view(), name="patient-appointments"),
    path("appointments/d/", views.AppointmentsForADoctorView.as_view(), name="doctor-appointments"),
    path("medHistory/", views.MedicalHistoryView.as_view(), name="med-history"),
    path("prescriptions/", views.PrescriptionListView.as_view(), name="doc-prescriptions"),
    path("prescription/create", views.PrescriptionCreateView, name="doc-prescriptions-create"),
    path("appointment/create", views.AppointmentCreateView, name="appointment-create"),
    path("rdashboard/", views.rdashboard, name="r_dashboard"),
    path("hrdashboard/", views.hrdashboard, name="hr_dashboard"),
    path("hraccounting/", views.hraccounting, name="hr_accounting"),
    path("payments/", views.pateintpayments, name="pat_payments"),
    #path('patient_invoice/', views.patient_invoice, name='patient_invoice'),
    path('get_pdf/(?P<id>\d+)/$', views.get_pdf, name='get_pdf'),
    path('send_reminder/(?P<id>\d+)/$', views.send_reminder, name='send_reminder'),
]


