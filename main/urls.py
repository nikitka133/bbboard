from django.urls import path, include
from django.views.decorators.cache import never_cache
from django.views.static import serve

from bbboard import settings
from main import views
from main.views import by_rubric, detail, index_bb_detail, profile_bb_detail, profile_bb_add, profile_bb_change, \
    profile_bb_delete

urlpatterns = [
    path('', views.index, name="index"),
    path('<int:pk>/', by_rubric, name="by_rubric"),
    path('page/<str:page>/', views.other_page, name="other"),
    path('accounts/login/', views.BBLoginView.as_view(), name="login"),
    path('accounts/profile/', views.profile, name="profile"),
    path('accounts/profile/<int:pk>/', profile_bb_detail, name='profile_bb_detail'),
    path('accounts/profile/change/', views.ChangeUserInfoView.as_view(), name="change"),
    path('accounts/logout/', views.BBLogout.as_view(), name="logout"),
    path('accounts/password/change/', views.BBPasswordChangeView.as_view(), name="password_change"),
    path('accounts/register/done/', views.RegisterDoneView.as_view(), name="register_done"),
    path('accounts/register/', views.RegisterUserView.as_view(), name="register"),
    path('accounts/register/activate/<str:sign>', views.user_activate, name="register_activate"),
    path('accounts/delete/', views.DeleteUserView.as_view(), name="delete"),
    path('detail/<int:pk>/', index_bb_detail, name="index_detail"),
    path('<int:rubric_pk>/<int:pk>/', detail, name="detail"),
    path('accounts/profile/add/', profile_bb_add, name='profile_bb_add'),
    path('acoounts/profile/change/<int:pk>/', profile_bb_change, name='profile_bb_change'),
    path('accounts/profile/delete/<int:pk>/', profile_bb_delete, name='profile_bb_delete'),

]
if settings.DEBUG:
    urlpatterns.append(path('static/<path:path>', never_cache(serve)))
