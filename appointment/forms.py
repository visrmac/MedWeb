from django import forms
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ('patient', 'symptoms', 'prescription')

    def __init__(self, *args, **kwargs):
        super(PrescriptionForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['patient'].queryset = User.objects.filter(user_type="P")


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['patient'].queryset = User.objects.filter(user_type="P")
            self.fields['doctor'].queryset = User.objects.filter(user_type="D")
            self.fields["date"].label = "Date (YYYY-MM-DD)"
            self.fields["time"].label = "Time 24 hr (HH:MM)"

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'
        payment_type = forms.CharField(
            max_length=1,
            widget=forms.Select(choices=PAYMENT_TYPES),)

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['patient'].queryset = User.objects.filter(user_type="P")
            self.fields["date"].label = "Date (YYYY-MM-DD)"
            self.fields["paid"].label = "New paid Label"
            self.fields['outstanding'].label = "New outstanding Label"