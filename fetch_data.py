import requests
from datetime import datetime, timedelta

def fetch_air_quality_data(api_key, city):
    geocoding_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(geocoding_url)
    if response.status_code == 200:
        city_data = response.json()
        lat = city_data['coord']['lat']
        lon = city_data['coord']['lon']
    else:
        return None, None

    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and 'list' in data:
        aqi = data['list'][0]['main']['aqi']
        pollutants = data['list'][0]['components']
        return aqi, pollutants
    else:
        return None, None


def fetch_air_quality_news(api_key):
    # URL for fetching air quality related news
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q=air quality OR air pollution&"
        f"language=en&"
        f"sortBy=publishedAt&"
        f"apiKey={api_key}"
    )
    response = requests.get(url)
    
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get("articles", [])
        news = []
        
        for article in articles[:5]:  # Limit to top 5 articles
            news.append({
                "title": article["title"],
                "description": article.get("description", ""),
                "url": article["url"]
            })
        return news
    else:
        return None
    


def fetch_historical_pollutant_data(api_key, city, pollutant):
    geocoding_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(geocoding_url)
    if response.status_code != 200:
        return []

    city_data = response.json()
    lat = city_data['coord']['lat']
    lon = city_data['coord']['lon']

    data_points = []
    now = datetime.utcnow()

    for i in range(1, 6):
        timestamp = int((now - timedelta(days=i)).replace(hour=12, minute=0, second=0).timestamp())
        url = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={timestamp}&end={timestamp + 3600}&appid={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'list' in data and data['list']:
                level = data['list'][0]['components'].get(pollutant, None)
                date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
                if level is not None:
                    data_points.append((date, round(level, 2)))

    return list(reversed(data_points))
