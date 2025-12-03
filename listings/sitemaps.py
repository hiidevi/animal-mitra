from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return [
            'listings:home',
            'listings:privacy_policy',
            'accounts:login',
            'accounts:register',
        ]

    def location(self, item):
        return reverse(item)


class HomeSitemap(Sitemap):
    """Sitemap for homepage with highest priority"""
    priority = 1.0
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ['listings:home']

    def location(self, item):
        return reverse(item)
