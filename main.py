import requests
import argparse
import sys


from rich.console import Console
from rich.table import Table

console = Console()

# url = "https://api.open-meteo.com/v1/forecast"
# params = {
# 	"latitude": 52.5244,
# 	"longitude": 13.4105,
# 	"hourly": "temperature_2m",
# }

# r = requests.get(url, params = params)
# print(r.json())

GEO_URL = 'https://geocoding-api.open-meteo.com/v1/search'


def find_city(name):
    """Return (name, country, lat, lon) for the best match or None"""

    r = requests.get(GEO_URL, params={"name": name, "count": 1}, timeout=10)
    r.raise_for_status()

    results = r.json().get('results')


    if not results:
        return None

    c = results[0]

    return c['name'], c.get('country', ''), c['latitude'], c['longitude']


#print(find_city('Berlin'))



WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather(lat, lon, fahrenheit=False):
    """Return the 'current_weather' dict for a coordinate."""
    params = {"latitude": lat, "longitude": lon, "current_weather": True}
    if fahrenheit:                                   # optional unit switch
        params["temperature_unit"] = "fahrenheit"
    r = requests.get(WEATHER_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()["current_weather"]


# name, country, lat, lon = find_city('Berlin') # type: ignore
# #print(get_weather(lat, lon))
# w = get_weather(lat, lon)

# print(f'Weather in {name}, {country}: {w['temperature']} C, wind {w['windspeed']} km/h')



def main():
    parser = argparse.ArgumentParser(description="Current weather for a city")
    parser.add_argument("city", help="City name, e.g. London")
    parser.add_argument("-f", "--fahrenheit", action="store_true", help="Use °F")
    args = parser.parse_args()

    try:
        place = find_city(args.city)
        if place is None:
            console.print(f"[red]City '{args.city}' not found.[/red]")
            sys.exit(1)
        name, country, lat, lon = place
        w = get_weather(lat, lon, args.fahrenheit)
    except requests.RequestException as e:
        console.print(f"[red]Network error:[/red] {e}")
        sys.exit(1)

    unit = "°F" if args.fahrenheit else "°C"
    table = Table(title=f"Weather in {name}, {country}")
    table.add_column("Temperature", style="cyan")
    table.add_column("Wind", style="green")
    table.add_column("Time", style="magenta")
    table.add_row(f"{w['temperature']} {unit}", f"{w['windspeed']} km/h", w["time"])
    console.print(table)

    
if __name__ == '__main__':
    main()