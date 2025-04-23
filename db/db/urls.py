"""
URL configuration for db project.

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
from django.urls import include, path
from users import views as user_views
from django.contrib.auth import views as authentication_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register,name='register'),
    path('login/',authentication_views.LoginView.as_view(template_name ='users/login.html'), name='login'), #class based view (that is why .asview())
    path('logout/',user_views.logout_view, name='logout_view'),
    path('cv_form/',user_views.cv_form, name='cv_form'),
    path('pdf/<int:id>',user_views.cv_pdf, name='cv_pdf'),
    path('list/',user_views.list, name='list'),
    path('cv/<int:id>',user_views.cv, name = 'cv'),
    path('redirect-to-cv/', user_views.redirect_to_cv, name='redirect_to_cv'),
]





from django.conf import settings
from django.conf.urls.static import static

urlpatterns += [ # += to add patterns to the images
    # ... the rest of your URLconf goes here ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)