from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator

from .scrapealgo import *

from .models import Movie, UserMovie
from .form import RegisterForm

import json
import time
# Create your views here.


def registerPage(request):
    registerForm = RegisterForm()
    if request.method == 'POST':
        registerForm = RegisterForm(request.POST)
        if registerForm.is_valid():
            registerForm.save()
            # user = registerForm.clean_data.get('username')
            # messages.success(request, 'Account was created for' + user)

            return redirect('login')

    context = {'form': registerForm}
    return render(request, 'register.html', context)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'username OR password is incorrect')

    context = {}
    return render(request, 'login.html', context)


def index(request):

    mov_obj = [mo for mo in Movie.objects.filter().order_by('?')[:3]]
    PAYLOAD = {'page_title': 'Scrape a movie',
               'latest_movies': mov_obj}
    return render(request, 'index.html', {'payload': PAYLOAD})


def progress(request):

    query = request.GET.get('query')

    PAYLOAD = get_request(request=request, query=query)

    with open('tmp.json', 'w') as wf:
        json.dump(PAYLOAD, wf, indent=2)

    return render(request, 'progress.html', {'payload': PAYLOAD})


def save(request):

    with open('tmp.json') as rf:
        PAYLOAD = json.load(rf)

    is_created = False
    # get movie from global database and save to local
    # check if movie exist locally before attempting to save
    payload_data = {mv for mv in PAYLOAD['scraped_data'].keys()}
    user_data = {
        mv.user_movie.moviename for mv in request.user.usermovie_set.all()}
    payload_not_in_user_data = payload_data.difference(user_data)

    if payload_not_in_user_data:
        for movie in payload_not_in_user_data:
            UserMovie.objects.create(
                user_movie=Movie.objects.get(moviename=movie),
                username=request.user
            )
            is_created = True
    else:
        is_created = False

    PAYLOAD = {'is_created': is_created, 'page_title': "Saved"}

    time.sleep(1)
    return redirect('browse')


def delete(request, moviename):

    toDelete = [m for m in request.user.usermovie_set.all()
                if moviename == m.user_movie.moviename]
    toDelete[0].delete()

    # wait for a while
    time.sleep(1)
    return redirect('my-scrapes')


def selectMovie(request, moviename):
    PAYLOAD = {}
    if moviename == 'progress':
        query = request.GET.get('query')
        PAYLOAD = get_request(request=request, query=query)
    else:
        movie_object = Movie.objects.get(moviename=moviename)
        PAYLOAD = fetch_from_db(movie_object)
        PAYLOAD['page_title'] = moviename

        if request.user.is_authenticated:
            isLocal = {movie_object.moviename}.difference(
                {m.user_movie.moviename for m in request.user.usermovie_set.all()})
            if isLocal:
                PAYLOAD['is_local'] = False
            else:
                PAYLOAD['is_local'] = True

        with open('tmp.json', 'w') as wf:
            json.dump(PAYLOAD, wf, indent=2)

    return render(request, 'progress.html', {'payload': PAYLOAD})


def myScrapes(request):

    category = request.GET.get('filter_by')
    category = 'All' if category == 'None' else category
    if category is None or category == 'All':
        user_mov_obj = [
            obj.user_movie for obj in request.user.usermovie_set.all().order_by('-id')]
    else:
        mov_obj = set(Movie.objects.filter(
            movie_type=category).order_by('-id'))
        user_movs = set(
            obj.user_movie for obj in request.user.usermovie_set.all())

        user_mov_obj = list(mov_obj.intersection(user_movs))
        user_mov_obj.reverse()

    total_movies_in_category = len(user_mov_obj)
    page_obj = Paginator(user_mov_obj, 6)
    current_page = request.GET.get('page') if request.GET.get('page') else 1
    current_page_obj = page_obj.get_page(current_page)

    total_pages = current_page_obj.paginator.num_pages
    PAYLOAD = {'movies': current_page_obj,
               'results_length': total_movies_in_category,
               'page_title': f"{str(request.user.username)}'s list | {current_page} of {total_pages}",
               'editable': True,
               'current_filter': category,
               }

    return render(request, 'browse.html', {'payload': PAYLOAD})


def browse(request):
    # using paginator to paginate
    category = request.GET.get('filter_by')
    category = 'All' if category == 'None' else category
    if category is None or category == 'All':
        mov_obj = Movie.objects.all().order_by('-id')
    else:
        mov_obj = Movie.objects.filter(movie_type=category).order_by('-id')

    if request.user.is_authenticated:  # display movies not saved by user
        user_movie_set = [
            m.user_movie for m in request.user.usermovie_set.all()]
        mov_obj = list(set(mov_obj).difference(set(user_movie_set)))
        mov_obj.reverse()

    total_movies_in_category = len(mov_obj)
    page_obj = Paginator(mov_obj, 9)
    current_page = request.GET.get('page') if request.GET.get('page') else 1
    current_page_obj = page_obj.get_page(current_page)

    total_pages = current_page_obj.paginator.num_pages
    PAYLOAD = {'movies': current_page_obj,
               'page_title': f"Page {current_page} of {total_pages}",
               'results_length': total_movies_in_category,
               'current_filter': category,
               }
    return render(request, 'browse.html', {'payload': PAYLOAD})

# special function to fetch data from database


def fetch_from_db(movie_object):
    '''
        parameter: a movie object from django.models
        manipulation: fetches the movie object details and parse them into a dictionary format
        return: returns a dictionary object with the elements of the movie object organized in the format:
                {'scraped_data':<something>, 'imglnk':<something>, 'is_local':<something>}
    '''

    movielink = movie_object.movielink.split(',')
    scraped_data = {movie_object.moviename: movielink}
    PAYLOAD = {
        'scraped_data': scraped_data,
        'imglnk': movie_object.imagelink,
        'movie_type': movie_object.movie_type,
    }
    return PAYLOAD


def save_global_db(PAYLOAD):
    if PAYLOAD['scraped_data']:
        for movie, links in PAYLOAD['scraped_data'].items():
            # check if movie is present before saving it.
            if movie not in [movie.moviename for movie in Movie.objects.all()]:
                Movie.objects.create(
                    query=PAYLOAD['query'],
                    moviename=movie,
                    movielink=", ".join(links),
                    imagelink=PAYLOAD['imglnk'],
                    movie_type=PAYLOAD['movie_type']
                )


def get_request(request, query):
    # if query exists fetch from database else scrape online
    # - need to have a special function that searches query from database:: movie queries or movie names

    PAYLOAD = {'scraped_data': '', 'imglnk': '', 'movie_type': '',
               'query': query, 'page_title': '', 'is_local': False}
    invalid_query = query.strip().replace("+", "") == ''
    # u: if for forced query
    if invalid_query:
        return PAYLOAD

    movie_obj_db = Movie.objects.filter(
        query__icontains=query) or Movie.objects.filter(moviename__icontains=query)
    query_found_in_db = len(movie_obj_db) != 0
    if query_found_in_db:
        title = 'Found in database'
        # core properties of payload
        first_obj = fetch_from_db(movie_obj_db[0])
        PAYLOAD['imglnk'] = "https://miro.medium.com/max/2160/0*WFJUV6w1MGI32y1P" if len(
            first_obj['imglnk']) < 5 else first_obj['imglnk']
        PAYLOAD['scraped_data'] = first_obj['scraped_data']
        PAYLOAD['movie_type'] = first_obj['movie_type']

        if request.user.is_authenticated:
            isLocal = {movie_obj_db}.difference(
                {m.user_movie for m in request.user.usermovie_set.all()})
            if isLocal:
                PAYLOAD['is_local'] = False
            else:
                PAYLOAD['is_local'] = True

        # fetch from database in desired format and create a merged desired format
        for index in range(1, len(movie_obj_db)):
            # check if global movie is also local
            PAYLOAD['scraped_data'].update(fetch_from_db(
                movie_obj_db[index])['scraped_data'])

    else:
        query = query[2:] if 'u:' in query else query
        movie_type = request.GET.get('movie-type')
        PAYLOAD['movie_type'] = movie_type

        try:
            if query.strip().replace("+", "") == '':    # if query is empty, return nothing
                scraped_data = {}
            else:
                # make address based on movie type
                address, movieKeyword = getAddress(movie_type, query)
                scraped_data = recursiveScrape(
                    find_tag('a', scrape(address)), movieKeyword.lower())
        except:
            scraped_data = {}

        # option to download image
        # download_img = request.GET.get('download-img')
        # if download_img == 'yes':
        #     try:
        #         print('='*50)
        #         imglnk = IMDB(query)
        #     except:
        #         print("COULD NOT OBTAIN IMAGE FILE")
        #         imglnk = "https://miro.medium.com/max/2160/0*WFJUV6w1MGI32y1P"
        # else:
        #     imglnk = "https://miro.medium.com/max/2160/0*WFJUV6w1MGI32y1P"

        # save not found queries

        imglnk = "#"
        if not scraped_data:
            title = "Not found"
            with open('notfoundlist', 'a+') as nfl:
                nfl.write(f"\n* - Query: {query:20} - Type: {movie_type:20}")
        else:
            title = "Scraped"
        # clean scraped data. remove all empty links
        scraped_data = {k: v for k, v in scraped_data.items() if v}
        PAYLOAD.update({'scraped_data': scraped_data,
                        'query': query,
                        'imglnk': imglnk,
                        'movie_type': movie_type,
                        'page_title': f"{query} | {title}"
                        })

        # save to global database
        save_global_db(PAYLOAD=PAYLOAD)

    return PAYLOAD
