import json
import requests
import os

# class die het makkelijker maakt om met timeslots te werken.
class timeslot():
    # data = timeslot dict die in openweather lijst zit
    def __init__(self, data):
        self.data = data

    def get_datum(self):
        return self.data.get("dt_txt")[0:10]

    # haalt rain en snow (rain is niet meer nodig maar dit kwam uit vorige code
    def __get_item(self, name):
        if self.data.get(name) is not None:
            return self.data.get(name).get("3h")
        return 0.0

    # Haalt dingen zoals bv. temperatuur.
    def __get_main_item(self, name):
        return self.data.get("main").get(name)

    def get_rain(self):
        return self.__get_item("rain")

    # Gebruikt de functie __get_item() om het aantal sneeuw op te halen.
    def get_snow(self):
        return self.__get_item("snow")

    def get_min_temp(self):
        return self.__get_main_item("temp_min")

    def get_max_temp(self):
        return self.__get_main_item("temp_max")

    # Gebruikt de functie __get_main_item() om de temperatuur op te halen.
    def get_temp(self):
        return self.__get_main_item("temp")

# class die Openweather data per locatie bijhoudt en functies defined die we nodig hebben om de mail te schrijven (+extra)
class weather():
    def __init__(self, loc, coord, open_weather_response):
        self.loc = loc
        self.coord = coord
        self.open_weather_response = open_weather_response
        self.timeslots = []
        for data in self.open_weather_response.get("list"):
            self.timeslots.append(timeslot(data))
        self.round_digits = 4

    # Een functie die alles afrond
    def set_round_digits(self, v):
        self.round_digits = v

    # Deze functie voert het afronden echt uit
    def __round_result(self, r):
        return round(r,self.round_digits)

    # Deze functie haalt de naam van de locatie op
    def get_location_name(self):
        return self.loc

    def min_temp_week(self):
        min_temp_week = self.timeslots[0].get_min_temp()
        for ts in self.timeslots:
            if ts.get_min_temp() < min_temp_week:
                min_temp_week = ts.get_min_temp()
        return self.__round_result(min_temp_week)

    def max_temp_week(self):
        max_temp_week = self.timeslots[0].get_max_temp()
        for ts in self.timeslots:
            if ts.get_max_temp() < max_temp_week:
                max_temp_week = ts.get_max_temp()
        return self.__round_result(max_temp_week)

    # Functie om de gemiddelde temperatuur van de week te berekenen.
    def avg_temp_week(self):
        t = 0.0
        for ts in self.timeslots:
            t += ts.get_temp()
        t = t / len(self.timeslots)
        return self.__round_result(t)

    # Functie om het aantal sneeuw per week op te tellen.
    def snow_week(self):
        s = 0.0
        for ts in self.timeslots:
            s += ts.get_snow()
        return self.__round_result(s)

    # Deze functie berekent de booking.com aanraderscore.
    def get_aanraderscore(self):
        score = 0
        if self.avg_temp_week() < 0:
            score = 5
        elif 0 < self.avg_temp_week() < 5:
            score = 4
        elif 5 < self.avg_temp_week() < 10:
            score = 3
        elif self.avg_temp_week() > 10:
            score = 1
        if self.snow_week() >= 5 and score < 5:
            score += 1
        return score

############################################################

# de dictionary met alle latitudes en longitudes van de locaties
locations = {
    "Les Trois Vallées": {"lat": 45.3356, "lon": 6.5890},
    "Sölden": {"lat": 46.9701, "lon": 11.0078},
    "Chamonix-Mont Blanc": {"lat": 45.9237, "lon": 6.8694},
    "Val di Fassa": {"lat": 46.4265, "lon": 11.7684},
    "Salzburger Sportwelt": {"lat": 47.3642, "lon": 13.4639},
    "Alpenarena Flims-Laax-Falera": {"lat": 46.8315, "lon": 9.2663},
    "Kitzsteinhorn Kaprun": {"lat": 47.1824, "lon": 12.6912},
    "Ski Arlberg": {"lat": 47.43346, "lon": 8.42053},
    "Espace Killy": {"lat": 45.4481, "lon": 6.9806},
    "Spindleruv Mly": {"lat": 50.7296, "lon": 15.6075}
}

print("Getting data from OpenWeather API...")
weather_data = []
#dit called de API voor elke locatie.
for loc, coord in locations.items():
    lat = coord.get("lat")
    lon = coord.get("lon")
    response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid=bbc71d0c3567c74e05b50bdff72f635b&units=metric")
    weather_data.append(weather(loc, coord, response.json()))

print("Making mail...")
mail = ""
for w in weather_data:
    w.set_round_digits(2)
    location_info = f"""
    {w.loc}:
        Snow: {w.snow_week()} cm
        Average Temperature: {w.avg_temp_week()} °C
        Aandraderscore: {w.get_aanraderscore()}/5
    """
    mail += location_info
