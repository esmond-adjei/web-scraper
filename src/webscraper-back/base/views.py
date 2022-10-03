from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def progress(request):
    query = request.GET['query']
    movie_type = request.GET['movie-type']
    download_img = request.GET['download-img']
    form_data = [query, movie_type, download_img]
    print(form_data)
    return render(request, 'progress.html',{"data": query})