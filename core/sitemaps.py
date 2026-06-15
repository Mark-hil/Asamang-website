from django.contrib import sitemaps
from django.urls import reverse

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'core:home', 
            'core:about', 
            'core:services', 
            'core:doctors', 
            'core:contact', 
            'core:appointment', 
            'core:faq',
            'core:terms',
            'core:privacy'
        ]

    def location(self, item):
        return reverse(item)
