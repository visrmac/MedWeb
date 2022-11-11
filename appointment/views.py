from django.conf.global_settings import EMAIL_HOST_USER
from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from user_profile.models import UserProfile
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import get_template
from io import BytesIO
import xhtml2pdf.pisa as pisa



# Create your views here.

class AppointmentsForAPatientView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'account:login'

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)


class AppointmentsForADoctorView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'account:login'

    def get_queryset(self):
        return Appointment.objects.filter(doctor=self.request.user)


class MedicalHistoryView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'account:login'

    def get_queryset(self):
        return Prescription.objects.filter(patient=self.request.user)


class PrescriptionListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'account:login'

    def get_queryset(self):
        return Prescription.objects.filter(doctor=self.request.user)





@login_required(login_url='/login/')
def PrescriptionCreateView(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = request.user
            prescription.save()
            return redirect('appointment:doc-prescriptions')
    else:
        form = PrescriptionForm()
    return render(request, 'appointment/prescription_create.html', {'form': form})


@login_required(login_url='/login/')
def AppointmentCreateView(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.save()
            return redirect('appointment:r_dashboard')
    else:
        form = AppointmentForm()
    return render(request, 'appointment/appointment_create.html', {'form': form})


@login_required(login_url='/login/')
def rdashboard(request):
    if request.method == "GET" and request.user.user_type == "R":
        context = {
            "totalApp": len(Appointment.objects.all()),
            "compApp": len(Appointment.objects.filter(status="Completed")),
            "pendApp": len(Appointment.objects.filter(status="Pending")),
            "app_list": Appointment.objects.all(),
            "pat_list": UserProfile.objects.filter(user__user_type="P")[:5]
        }
        return render(request, 'appointment/r_dashboard.html', context=context)


@login_required(login_url='/login/')
def hrdashboard(request):
    if request.method == "GET" and request.user.user_type == "HR":
        context = {
            "totalPat": len(User.objects.filter(user_type="P")),
            "totalDoc": len(User.objects.filter(user_type="D")),
            "ondutyDoc": len(UserProfile.objects.filter(status="Active").filter(user__user_type="D")),
            "doc_list": UserProfile.objects.filter(user__user_type="D")
        }
        return render(request, 'appointment/hr_dashboard.html', context=context)

'''
@login_required(login_url='/login/')
def hraccounting(request):
    if request.method == "GET" and request.user.user_type == "HR":
        context = {
            "payment_ind": Payment.objects.filter(payment_type="I"),
            "payment_cons": Payment.objects.filter(payment_type="C"),
        }
        return render(request, 'appointment/accounting.html', context=context)


@login_required(login_url='/login/')
def pateintpayments(request):
    if request.method == "GET":
        context = {
            "payment_me": Payment.objects.filter(patient=request.user),
        }
        return render(request, 'appointment/payment_invoice.html', context=context)
'''
@login_required(login_url='/login/')
def hraccounting(request):
    status = False
    if request.user:
        status = request.user
    individual = Invoice.objects.all()
    consulation = Prescription.objects.all()

    return render(request, 'appointment/accounting.html',
                  {'individual': individual, 'consulation': consulation, 'user': 'HR', 'status': status})




# Upadate Status
@login_required(login_url='/login/')
def update_status(request, id):
    print(id)
    status = False
    if request.user:
        status = request.user
    if request.method == "POST":
        data = Appointment.objects.get(id=id)
        pers = Prescription.objects.get(appointment=data)
        pers.outstanding = request.POST['outstanding']
        pers.paid = request.POST['paid']
        pers.total = int(request.POST['outstanding']) + int(request.POST['paid'])
        pers.save()
        data.status = 1
        data.save()
        return redirect('r_dashboard')

    return render(request, 'appointment/update_status.html', { "id": id, 'status': status})

# Patient payment
@login_required(login_url='/login/')
def pateintpayments(request):
    if request.method == "GET":
        context = {
            "payment_me": Payment.objects.filter(patient=request.user),
        }
        return render(request, 'appointment/payment_invoice.html', context=context)


#  Invoice Generator
def get_pdf(request, id):
    data = PrescriptionForm.objects.get(id=id)
    pdf_data = {'data': data}
    template = get_template('invoice.html')
    data_p = template.render(pdf_data)
    response = BytesIO()
    pdf_page = pisa.pisaDocument(BytesIO(data_p.encode('UTF_8')), response)
    if not pdf_page.err:
        return HttpResponse(response.getvalue(), content_type='application/pdf')
    else:
        return HttpResponse('Error')


# Send Reminder
def send_reminder(request, id):
    p = PrescriptionForm.objects.get(id=id)
    email = p.patient.email
    subject = 'Payment Reminder '
    message = 'Your Due Amount is {} outstanding and {} rs. you have already paid'.format(p.outstanding, p.paid)
    recepient = [email]
    send_mail(subject, message, EMAIL_HOST_USER, recepient, fail_silently=False)
    return redirect('accounting')
