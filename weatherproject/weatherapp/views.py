from django.shortcuts import render
from django.contrib import messages
import requests
import datetime


def get_city_image(city_name):
    """Fetch an image for the city from Pixabay API"""
    try:
        pixabay_api_key = '45130658-4c13b34bab88d9ad4a5d5df47'
        pixabay_url = f'https://pixabay.com/api/?key={pixabay_api_key}&q={city_name}&image_type=photo&per_page=3&safesearch=true&order=popular'
        response = requests.get(pixabay_url, timeout=5)
        data = response.json()
        
        if data.get('hits') and len(data['hits']) > 0:
            # Return the first image's full quality URL
            img_url = data['hits'][0]['largeImageURL']
            # Add timestamp to prevent caching
            return f'{img_url}?t={int(datetime.datetime.now().timestamp())}'
        else:
            # Fallback to a generic landscape image
            return f'https://via.placeholder.com/1200x800?text={city_name}'
    except Exception as e:
        # Fallback image if API call fails
        return f'https://via.placeholder.com/1200x800?text={city_name}'


def home(request):
    if 'city' in request.POST:
        city = request.POST['city']
    else:
        city = 'London'

    # OpenWeatherMap API
    api_key = '4ad312810ffbfcbde35e0f993d759a39'
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

    try:
        data = requests.get(url).json()
        
        # Check if city was found
        if data.get('cod') != 200:
            messages.error(request, f'City "{city}" not found')
            return render(request, 'weatherapp/index.html', {
                'exception_occurred': True,
                'city': city,
                'background_image': get_city_image('mountains')
            })
        
        description = data['weather'][0]['description']
        icon = data['weather'][0]['icon']
        temp = data['main']['temp']
        city_name = data['name']  # Use actual city name from API
        day = datetime.date.today()
        
        # Get city image
        background_image = get_city_image(city_name)

        return render(request, 'weatherapp/index.html', {
            'description': description,
            'icon': icon,
            'temp': temp,
            'day': day,
            'city': city_name,
            'exception_occurred': False,
            'background_image': background_image
        })

    except Exception as e:
        messages.error(request, f'Error fetching weather data: {str(e)}')
        return render(request, 'weatherapp/index.html', {
            'exception_occurred': True,
            'city': city,
            'background_image': get_city_image('sky')
        })