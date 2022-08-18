# Register your models here.

from django.contrib import admin
import datetime

from .forms import SubRubricForm
from .models import AdvUser, SuperRubric, SubRubric, AdditionalImage, Bb
from .utilities import send_activation_notification


# from .models import SuperRubric, SubRubric
#
#
def send_activation_notifications(modeladmin, request, queryset):
    print(queryset)
    send_activation_notifications.short_description = "Отправка писем с требованиями активации"
    for rec in queryset:
        print(rec.is_active)
        if not rec.is_active:
            send_activation_notification(rec)
            modeladmin.message_user(request, "Письма с требованиями отправлены")

        else:
            modeladmin.message_user(request, "Пользователь активирован")


#
#
class NonactivatedFilter(admin.SimpleListFilter):
    title = "Прошли активацию?"
    parameter_name = "actstate"

    def lookups(self, request, model_admin):
        return (
            ("activated", "Прошли активацию"),
            ("threedays", "He прошли более 3 дней"),
            ('week', "He прошли более недели")
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == "activated":
            return queryset.filter(is_active=True, )

        elif val == "threedays":
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, date_joined__date__lt=d)

        elif val == "week":
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, date_joined__date__lt=d)


class AdvUserAdmin(admin.ModelAdmin):
    list_display = ("date_joined", "is_active", "username", "email", "first_name", "last_name", "last_login",)
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = (NonactivatedFilter,)
    # fields = (
    #     ("username", "email"), ("first_name", "last_name"),
    #     ("send—messages", "is_active",),
    #     ("is_staff", "is_superuser"),
    #     "groups", "user_permissions",
    #     ("last_login", "date_joined")
    # )
    readonly_fields = ("last_login", "date_joined")
    actions = (send_activation_notifications,)


class SubRubricinline(admin.TabularInline):
    model = SubRubric


class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ("super_rubric",)
    inlines = (SubRubricinline,)


class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage


class BbAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', "content", "author", "created_at")
    fields = (('rubric', "author"), "title", 'content', 'price', "contacts", 'image', "is_active")
    inlines = (AdditionalImageInline,)


admin.site.register(SubRubric, SubRubricAdmin)
admin.site.register(SuperRubric, SuperRubricAdmin)
admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(Bb, BbAdmin)

