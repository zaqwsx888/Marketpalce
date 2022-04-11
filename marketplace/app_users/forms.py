from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'e-mail'
        self.fields['password'].label = _('Пароль')

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = User.objects.filter(email=email).first()
        if not user:
            raise forms.ValidationError(
                f'{_("Пользователь с")} {email} {_("не найден.")}'
            )
        if not user.check_password(password):
            raise forms.ValidationError(_('Неверный пароль'))
        return self.cleaned_data


class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(
        label=_('Пароль еще раз'),
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html)
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html)
    phone = forms.CharField(label=_('Телефон'), required=False)
    email = forms.EmailField()

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) != 18:
            raise forms.ValidationError(_('Не верный телефон'))
        return ''.join([phone[4:7], phone[9:12], phone[13:15], phone[16:18]])

    def clean_email(self):
        email = self.cleaned_data['email']
        domain = email.split('.')[-1]
        if domain in ['net', 'xyz']:
            raise forms.ValidationError(
                f'{_("Регистрация через домен")}'
                f' {domain} {_("невозможна")}'
            )
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _('Этот email уже используется')
            )
        return email

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают')
        password_validation.validate_password(self.cleaned_data['password'],
                                              None)
        return self.cleaned_data

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'email',
            'password', 'confirm_password'
        ]


class EditProfileForm(forms.ModelForm):
    fio = forms.CharField(required=True)
    phone = forms.CharField(required=False)
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, required=False
    )
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = [
            'avatar', 'fio', 'phone', 'email', 'password',
            'confirm_password'
        ]

    def clean_email(self):
        email = self.cleaned_data['email']
        domain = email.split('.')[-1]
        if domain in ['net', 'xyz']:
            raise forms.ValidationError(
                f'{_("Регистрация через домен")}'
                f' {domain} {_("невозможна")}'
            )
        if self.instance.email != email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    _('Этот email уже используется')
                )
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) != 18:
            raise forms.ValidationError(_('Не верный телефон'))
        return ''.join([phone[4:7], phone[9:12], phone[13:15], phone[16:18]])

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError(_('Пароли не совпадают'))
        return self.cleaned_data
