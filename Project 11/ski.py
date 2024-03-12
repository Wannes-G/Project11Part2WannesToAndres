import json
import requests

# De inputq voor de temp en de regen dat de tourist zou willen
desired_temp = int(input("Whats youre desired temperature(write the number): "))
rain_tolerance = int(input(f"Whats youre desired rain per mm:\n1)Zeer weining(minder als 1m)\n2)Gemiddeld regen(1mm-2mm)\n3)Geen voorkeur(2mm)\nWrite the number: "))
if rain_tolerance == 1:
    rain_tolerance = "Zeer weining regen"
if rain_tolerance == 2:
    rain_tolerance = "Minder dan 2mm per dag"
if rain_tolerance == 3:
    rain_tolerance = "Meer als 2mm regen"
# class die het makkelijker maakt om met timeslots te werken.
class timeslot():
    # data = timeslot dict die in openweather lijst zit
    def __init__(self, data):
        self.data = data


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

    # Het regen in de week (5dagen)
    def avg_rain_week(self):
        r = 0.0
        for ts in self.timeslots:
            r += ts.get_rain()
        r = r / 5
        return self.__round_result(r)

    # Het printen van het aantel regen dat er wal vallen in de week
    def rain_score(self):
        if self.avg_rain_week() < 0.10:
            return "Zeer weining regen"
        elif 0.10 < self.avg_rain_week() < 0.20:
            return "Minder dan 2mm per dag"
        elif self.avg_rain_week() > 0.20:
            return "Meer als 2mm regen"





    # Functie om de gemiddelde temperatuur van de week te berekenen.
    def avg_temp_week(self):
        t = 0.0
        for ts in self.timeslots:
            t += ts.get_temp()
        t = t / len(self.timeslots)
        return self.__round_result(t)


    # Deze functie berekent de booking.com aanraderscore.
    def get_tempscore(self):
        score = 0
        if abs(self.avg_temp_week() - desired_temp) <= 2:
            score = 5
        elif 2 > abs(self.avg_temp_week() - desired_temp) <= 3:
            score = 4
        elif 3 > abs(self.avg_temp_week() - desired_temp) <= 5:
            score = 3
        elif 5 > abs(self.avg_temp_week() - desired_temp) <= 7:
            score = 2
        elif 7 > abs(self.avg_temp_week() - desired_temp) <= 10:
            score = 1

        return score

    # hoe dat de score voor de regen werkt
    def get_rainscore(self):
        rainscore = 0
        if rain_tolerance == self.rain_score():
            rainscore += 4
        else:
            rainscore = 0

        return rainscore

    def sum(self):
        self.get_tempscore() + self.get_rainscore()





############################################################

# de dictionary met alle latitudes en longitudes van de locaties
locations = {
     "Ankara Turkije": {"lat": 39.9334, "lon": 32.8597},
     "Athene Griekeland": {"lat": 37.9838, "lon": 23.7275},
     "La Valette, Malta": {"lat": 35.8992, "lon": 14.5141},
     "Sardinië, Italië": {"lat": 40.1209, "lon": 9.0129},
     "Sicilië, Italië": {"lat": 37.3979, "lon": 14.6588},
     "Nicosia, Cyprus": {"lat": 35.1856, "lon": 33.3823},
     "Mallorca, Spanje": {"lat": 39.6953, "lon": 3.0176},
     "Lagos, Portugal": {"lat": 37.1028, "lon": 8.6730},
     "Mauritius": {"lat": 20.3484, "lon": 57.5522},
     "Boekarest, Roemenië": {"lat": 44.4268, "lon": 26.1025}
 }

# berekend de score dat de locatie krijgt
def calculate_sum(w):
    w.set_round_digits(2)
    return w.get_tempscore() + w.get_rainscore()

print("Getting data from OpenWeather API...")
weather_data = []

#dit called de API voor elke locatie.
for loc, coord in locations.items():
    lat = coord.get("lat")
    lon = coord.get("lon")
    response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid=bbc71d0c3567c74e05b50bdff72f635b&units=metric")
    weather_data.append(weather(loc, coord, response.json()))

# Ordend de locaties van hoogste sum naar laagste.
weather_data = sorted(weather_data, key=calculate_sum, reverse=True)

print("Making mail...")
mail = ""
for w in weather_data:
    w.set_round_digits(2)
    location_info = f"""
    {w.loc}:

        Average Temperature: {w.avg_temp_week()} °C
        Average Rainfall: {w.rain_score()} 
    """

    mail += location_info
