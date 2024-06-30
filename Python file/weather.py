from datetime import datetime
import os
from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

API_KEY = os.getenv('API_KEY','475ea97761d8d3959bfe40ab3b77')
DEFAULT_CITY = 'London'

def get_weather_data(city):
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
        response = requests.get(url)
        response.raise_for_status()  
        return response.json()
    except requests.RequestException as e:
        return {'error': str(e)}

def preprocess_name(input_text):
    
    introduction_phrases = ["my name is", "i am", "i'm","My name's","You can call me","I go by","They call me"]
    for phrase in introduction_phrases:
        if input_text.lower().startswith(phrase):
            input_text = input_text[len(phrase):].strip()
            break
    
    words = input_text.split()
    
    
    if len(words) > 1 and re.match(r'^[A-Z]\.?$', words[0], re.IGNORECASE):
        
        return words[1]
    
    
    return words[0]


def capitalize_first_letter(word):
    return word.capitalize()

def convert_unix_to_readable(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    city = data.get('city', DEFAULT_CITY)
    
    if 'input' in data:
        processed_name = preprocess_name(data['input'])
        return jsonify({'processed_name': processed_name}), 200
    
    if 'word' in data:
        capitalized_word = capitalize_first_letter(data['word'])
        return jsonify({'capitalized_word': capitalized_word}), 200
    
    weather_data = get_weather_data(city)
    location = weather_data.get('name')
    description = weather_data['weather'][0]['description']
    temperature = weather_data['main']['temp']
    
    chatbot_response = f"The weather in {location} is currently {description} with a temperature of {temperature}°C."
    
    if 'weather' not in weather_data:
        return jsonify({'error': f'Sorry, I could not find weather data for {city}. Please check the city name.'}), 400

    return jsonify({
        'location': weather_data.get('name'),
        'temperature': weather_data['main']['temp'],
        'description': weather_data['weather'][0]['description'],
        'weather_icon': weather_data['weather'][0]['icon'],
        'humidity': weather_data['main']['humidity'],
        'pressure': weather_data['main']['pressure'],
        'wind_speed': weather_data['wind']['speed'],
        'wind_direction': weather_data['wind']['deg'],
        'cloudiness': weather_data['clouds']['all'],
        'visibility': weather_data.get('visibility', 'N/A'),
        'sunrise': convert_unix_to_readable(weather_data['sys']['sunrise']),
        'sunset': convert_unix_to_readable(weather_data['sys']['sunset']),
        'feels_like': weather_data['main']['feels_like'],
        'chatbot_response': chatbot_response,
        'response': 'Hello!😊'
    })

if __name__ == '__main__':
    app.run(debug=True)
