from django import forms
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView

from main.forms import BbForm, AiFormSet
from main.models import AdvUser, ChangeUserInfoForm, RegisterUserForm, SubRubric, Bb
from main.utilities import signer


def other_page(request, page):
    try:
        template = get_template("main/layout/" + page + ".html")
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


@login_required
def profile(request):
    bbs = Bb.objects.filter(author=request.user.pk)
    context = {'bbs': bbs}
    return render(request, "main/layout/profile.html", context)


class BBLoginView(LoginView):
    template_name = "main/layout/login.html"


class BBLogout(LoginRequiredMixin, LogoutView):
    template_name = "main/layout/logout.html"


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """Изменение дынных в профиле"""
    model = AdvUser
    template_name = "main/layout/change_user_info.html"
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy("main:profile")
    success_message = "Данные изменены"

    # получаем id пользователя
    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    """Изменение пароля"""
    template_name = "main/layout/password_change.html"
    success_url = reverse_lazy("main:profile")
    success_message = "Пароль изменен"


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = "main/layout/register_user.html"
    form_class = RegisterUserForm
    success_url = reverse_lazy("main:register_done")


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = "main/layout/delete_user.html"
    success_url = reverse_lazy("main:index")

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)

        messages.add_message(request, messages.SUCCESS, "Пользователь удален")
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()

        return get_object_or_404(queryset, pk=self.user_id)


class RegisterDoneView(TemplateView):
    template_name = "main/layout/register_done.html"


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, "main/layout/bad_signature.html")
    user = get_object_or_404(AdvUser, username=username)
    if user.is_active:
        template = "main/layout/user_is_activated.html"
        return render(request, template)
    else:
        template = "main/layout/activation_done.html"
        user.is_active = True
        user.is_activated = True
        user.save()
        return render(request, template)


def by_rubric(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    bbs = Bb.objects.filter(is_active=True, rubric=pk)
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bbs = bbs.filter(q)
    else:
        keyword = ""

    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'bbs': page.object_list,
               'form': form}
    return render(request, 'main/layout/by_rubric.html', context)


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label="")


def detail(request, rubric_pk, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    context = {"bb": bb, "ais": ais}
    return render(request, "main/layout/detail.html", context)


def index(request):
    bbs = Bb.objects.filter(is_active=True)[:10]
    context = {'bbs': bbs}
    return render(request, "main/layout/index.html", context)


def index_bb_detail(request, pk):
    bbs = get_object_or_404(Bb, pk=pk)
    context = {"bb": bbs}
    return render(request, "main/layout/detail.html", context)


@login_required
def profile_bb_detail(request, pk):
    bbs = get_object_or_404(Bb, pk=pk)
    context = {"bb": bbs}
    return render(request, "main/layout/user_bb_detail.html", context)


# Боже, что здесь твориться????
@login_required
def profile_bb_add(request):
    if request.method == "POST":
        form = BbForm(request.POST, request.FILES)
        if form.is_valid():
            bb = form.save()
            formset = AiFormSet(request.POST, request.FILES, instance=bb)

            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, "Объявление добавлено")
                return redirect('main:profile')
    else:
        form = BbForm(initial={'author': request.user.pk})
        formset = AiFormSet
        context = {'form': form, 'formset': formset}
        return render(request, 'main/layout/profile_bb_add.html', context)


@login_required
def profile_bb_change(request, pk):
    bb = get_object_or_404(Bb, pk=pk)

    if request.method == "POST":
        form = BbForm(request.POST, request.FILES, instance=bb)
        if form.is_valid():
            bb = form.save()
            formset = AiFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, "Объявление исправлено")
                return redirect('main:profile')
    else:
        form = BbForm(instance=bb)
        formset = AiFormSet(instance=bb)
        context = {'form': form, "formset": formset}
        return render(request, 'main/layout/profile_bb_change.html', context)


@login_required
def profile_bb_delete(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == "POST":
        bb.delete()
        messages.add_message(request, messages.SUCCESS, "Объявление удалено")
        return redirect("main:profile")
    else:
        context = {"bb": bb, }
        return render(request, "main/layout/profile_bb_delete.html", context)
