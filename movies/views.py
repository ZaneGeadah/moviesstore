from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})
def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    ratings = Rating.objects.filter(movie=movie)
    rating_stats = ratings.aggregate(average=Avg('stars'), count=Count('id'))
    user_rating = None
    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    if rating_stats['average'] is not None:
        template_data['average_rating'] = round(rating_stats['average'], 1)
    else:
        template_data['average_rating'] = None
    template_data['rating_count'] = rating_stats['count']
    template_data['user_rating'] = user_rating
    return render(request, 'movies/show.html', {'template_data': template_data})
@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)
@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, movie_id=id)
    review.delete()
    return redirect('movies.show', id=id)
@login_required
def rate_movie(request, id):
    movie = get_object_or_404(Movie, id=id)
    if request.method == 'POST':
        try:
            stars = int(request.POST.get('stars', ''))
        except ValueError:
            stars = 0
        if 1 <= stars <= 5:
            Rating.objects.update_or_create(
                movie=movie, user=request.user,
                defaults={'stars': stars})
    return redirect('movies.show', id=id)
@staff_member_required
def top_commenter(request):
    top_user = User.objects.annotate(num_comments = Count('review')).filter(num_comments__gt = 0).order_by('-num_comments').first()
    template_data = {}
    template_data['top_user'] = top_user
    return render(request, 'movies/top_commenter.html', {'template_data': template_data})    