from random import choice

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from .apps import user_registered

# Create your models here.
from .utilities import get_timestamp_path


class AdvUser(AbstractUser):
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Учетная запись активна?")
    send_message = models.BooleanField(default=True, verbose_name="Отправлять оповещение о комментариях?")

    def delete(self, *args, **kwargs):
        for bb in self.bb_set.all():
            bb.delete()
            super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass



class ChangeUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email!!!")

    class Meta:
        model = AdvUser
        fields = ("username", "email", "first_name", "last_name", "send_message")


class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")
    password1 = forms.CharField(label="Пароль",
                                widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label="Пароль повторно",
                                widget=forms.PasswordInput,
                                help_text="Пароль не совподают")

    def clean_password1(self):
        password1 = self.cleaned_data["password1"]
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            errors = {"password2": ValidationError("Введенные пароли не совподают", code="password_mismatch"),
                      "password1": ValidationError("Введенные пароли не совподают", code="password_mismatch")}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=True)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registered.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ("username", "email", "password1", "password2", "first_name", "last_name", "send_message")


class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name="Название")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name="Порядок")
    super_rubric = models.ForeignKey("SuperRubric", on_delete=models.PROTECT, null=True, blank=True,
                                     verbose_name="Надрубрика")


class SuperRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)


class SuperRubric(Rubric):
    objects = SuperRubricManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ("order", "name")
        verbose_name = "Надрубрика"
        verbose_name_plural = "Надрубрики"


class SubRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self):
        return "% s - % s" % (self.super_rubric.name, self.name)

    class Meta:
        proxy = True
        ordering = ("super_rubric__order", "super_rubric__name", "order", "name")
        verbose_name = "Подрубрика"
        verbose_name_plural = "Подрубрики"


class Bb(models.Model):
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT, verbose_name="Рубрика")
    title = models.CharField(max_length=40, verbose_name='Товар')
    content = models.TextField(verbose_name='Описание')
    price = models.FloatField(default=0, verbose_name='L[eHa')
    contacts = models.TextField(verbose_name='Контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Изображение')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Автор объявления')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-created_at']


class AdditionalImage(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name="Объявление")
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображение')

    class Meta:
        verbose_name_plural = "Дополнительные иллюстрации"
        verbose_name = "Дополнительная иллюстрация"
