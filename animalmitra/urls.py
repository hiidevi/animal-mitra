"""
Main URL Configuration for animalmitra project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from listings.sitemaps import StaticViewSitemap, HomeSitemap


# Sitemap configuration for SEO
sitemaps = {
    'static': StaticViewSitemap,
    'home': HomeSitemap,
}


urlpatterns = [
    # Django admin (built-in)
    path('admin/', admin.site.urls),
    
    # Homepage and listings
    path('', include('listings.urls')),
    
    # User authentication (login, register, logout)
    path('accounts/', include('accounts.urls')),
    
    # User dashboards
    path('dashboard/', include('dashboard.urls')),
    
    # Custom admin panel
    path('admin-panel/', include('admin_panel.urls')),
    
    # SEO URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),
]


# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
