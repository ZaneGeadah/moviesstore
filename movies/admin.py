from django.contrib import admin
from django.db.models import Count, Sum
from django.template.response import TemplateResponse
from django.urls import path


# Register your models here.
from .models import Movie, Review, Rating
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
    change_list_template = 'admin/movies/movie_change_list.html'
    def get_urls(self):
        custom_urls = [
            path('stats/', self.admin_site.admin_view(self.stats_view),
            name='movies_movie_stats'),
        ]
        return custom_urls + super().get_urls()
    def stats_view(self, request):
        most_bought = Movie.objects.annotate(
            times_bought = Sum('item__quantity')).filter(
            times_bought__gt=0).order_by('-times_bought').first()
        most_reviewed = Movie.objects.annotate(
            times_reviewed = Count('review')).filter(
            times_reviewed__gt=0).order_by('-times_reviewed').first()
        context = dict(
            self.admin_site.each_context(request),
            title='Movie stats',
            most_bought = most_bought,
            most_reviewed = most_reviewed,
        )
        return TemplateResponse(request, 'admin/movies/movie_stats.html', context)

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(Rating)
