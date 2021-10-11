from requests import get


# import pyowm
# owm = pyowm.OWM()
# obs = owm.weather_at_id(6173331)
# w = obs.get_weather()

# test variable
# rr = {"coord": {"lon": -123.12, "lat": 49.25}, "weather": [{"id": 500, "main": "Rain", "description": "light rain", "icon": "10n"}, {"id": 701, "main": "Mist", "description": "mist", "icon": "50n"}], "base": "stations", "main": {"temp": 277.05, "feels_like": 273.54, "temp_min": 274.26, "temp_max": 279.82, "pressure": 1024, "humidity": 100}, "visibility": 3219, "wind": {"speed": 3.1, "deg": 100}, "clouds": {"all": 90}, "dt": 1576549434, "sys": {"type": 1, "id": 761, "country": "CA", "sunrise": 1576512111, "sunset": 1576541665}, "timezone": -28800, "id": 6173331, "name": "Vancouver", "cod": 200}

# Documention: https://openweathermap.org/current
def getweather():
    rr = get("http://api.openweathermap.org/data/2.5/weather?id=6173331&APPID=6a5355d562381f240b2e68c6e7e42b99", timeout=2).json()

    woutput = "Weather for " + rr["name"] + ", " + rr["sys"]["country"] + ": "

    wdesc = []
    if "weather" in rr:
        for wid in rr["weather"]:
            wdesc.append(wid["description"])
        wdesc = ", ".join(wdesc)
        woutput += wdesc.capitalize() + "."

        wprecm = None
        wpreci = None
        if "rain" in rr:
            if "1h" in rr["rain"]:
                wprecm = rr["rain"]["1h"]
                wpreci = round(wprecm / 25.4, 2)
            elif "3h" in rr["rain"]:
                wprecm = rr["rain"]["3h"]
                wpreci = round(wprecm / 25.4, 2)
        elif "snow" in rr:
            if "1h" in rr["snow"]:
                wprecm = rr["snow"]["1h"]
                wpreci = round(wprecm / 25.4, 2)
            elif "3h" in rr["snow"]:
                wprecm = rr["snow"]["3h"]
                wpreci = round(wprecm / 25.4, 2)
        if wprecm is not None and wpreci is not None:
            woutput += " " + str(round(wprecm)) + "mm (" + str(wpreci) + "in)."

    if "feels_like" in rr["main"]:
        wtempm = round(rr["main"]["feels_like"] - 273.15)
        wtempi = round(rr["main"]["feels_like"] * 1.8 - 459.67)
        woutput += " Feels like " + str(wtempm) + "°C (" + str(wtempi) + "°F)"

    elif "temp" in rr["main"]:
        wtempm = round(rr["main"]["temp"] - 273.15)
        wtempi = round(rr["main"]["temp"] * 1.8 - 459.67)
        woutput += " " + str(wtempm) + "°C (" + str(wtempi) + "°F)"

    if "humidity" in rr["main"]:
        whumid = rr["main"]["humidity"]
        woutput += " with " + str(whumid) + "% humidity"

    if "wind" in rr:
        if "speed" in rr["wind"]:
            wwindm = round(rr["wind"]["speed"] * 3.6)
            wwindi = round(rr["wind"]["speed"] * 2.237136)
            woutput += " and " + str(wwindm) + "km/h (" + str(wwindi) + "mph) winds"
            if "deg" in rr["wind"]:
                wwinddeg = rr["wind"]["deg"]

                if 337.5 <= wwinddeg <= 360 or 0 <= wwinddeg < 22.5:
                    wwinddeg = "north"
                elif 22.5 <= wwinddeg < 67.5:
                    wwinddeg = "northeast"
                elif 67.5 <= wwinddeg < 112.5:
                    wwinddeg = "east"
                elif 112.5 <= wwinddeg < 157.5:
                    wwinddeg = "southeast"
                elif 157.5 <= wwinddeg < 202.5:
                    wwinddeg = "south"
                elif 202.5 <= wwinddeg < 247.5:
                    wwinddeg = "southwest"
                elif 247.5 <= wwinddeg < 292.5:
                    wwinddeg = "west"
                elif 292.5 <= wwinddeg < 337.5:
                    wwinddeg = "northwest"
                else:
                    wwinddeg = "unknown"

                woutput += " from the " + wwinddeg

    woutput += "."

    return woutput
