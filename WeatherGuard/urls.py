"""
URL configuration for WeatherGuard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from weather import views, userAdmin, notificationAdmin
from django.conf.urls.static import static
from django.conf import settings
from weather.guestHandler import HandleNotifyNowAPI


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.get_login, name="login"),
    path("user_login/", views.user_login, name="userlogin"),
    path("get_onboard/", views.get_register, name="get_onboard"),
    path("onboard/", views.RegisterAPIView.as_view(), name="onboard"),
    path("home/", views.get_home, name="home"),
    path("logout/", views.get_login, name="logout"),
    path("api/guest-login/", views.guest_login_api, name="guest_login_api"),
    path('geocode/', views.geocode_location, name='geocode_location'),
    path('await-verification/', views.verification_pending, name='await-verification'),
    path('verification_page/', views.get_verification, name='verification_page'),
    path("resend-email/", views.ResendEmailAPIView.as_view(), name="resend-email"),
    path('send-sms-verification-code/', views.SendSMSVerificationCodeView.as_view(), name='send-sms-verification-code'),
    path('verify-sms/', views.VerifySMSView.as_view(), name='verify-sms'),
    path('verification-form/', views.verification_form, name='verification-form'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify-email'),
    path('new-location/', userAdmin.AddLocationView.as_view(), name='add_location'),
    path('get-user-preferences/', userAdmin.GetUserPreferences.as_view(), name='get-preference'),
    path('set-user-preferences/', userAdmin.AlterUserPreferences.as_view(), name='set-preference'),
    # search
    path('api/search_location/', views.SearchLocation.as_view(), name='search_location'),
    # notify Apis
    path('api/notify-now/', HandleNotifyNowAPI.as_view(), name='notify-now'),
    path('hourly-now/', notificationAdmin.SendHourlyWeatherEmailAPIView.as_view(), name='hourly-notify'),
    path('daily-now/', notificationAdmin.SendDailyWeatherEmailsAPIView.as_view(), name='daily-notify'),
    path('weekly-now/', notificationAdmin.SendWeeklyWeatherEmailsAPIView.as_view(), name='daily-notify'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
