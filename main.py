from math import ceil

from fastapi import FastAPI
from pydantic import BaseModel
import requests


app = FastAPI(
    title="RideBuddy Budget Calculator API",
    description="Budget estimation service for RideBuddy Agent",
    version="1.0.0"
)

class BudgetRequest(BaseModel):
    distance_km: float
    trip_days: int
    vehicle_type: str
    travelers: int
    budget_type: str
    activity_level: str

FUEL_PRICE = 100

VEHICLE_MILEAGE = {
    "bike": 35,
    "car_petrol": 15,
    "car_diesel": 20
}

HOTEL_RATES = {
    "budget": 800,
    "mid": 2000,
    "luxury": 5000
}

FOOD_PER_PERSON = 500

ACTIVITY_COST = {
    "low": 300,
    "medium": 600,
    "high": 1000
}

MISC_PER_PERSON = 200




WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Light Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    80: "Rain Showers",
    81: "Heavy Rain Showers",
    82: "Violent Rain Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Hail",
    99: "Severe Thunderstorm"
}



def generate_travel_advice(
    temperature,
    weather_code,
    wind_speed,
    rain_probability
):
    
    condition = WEATHER_CODES.get(weather_code, "Unknown")

    advice = []

    if temperature >= 35:
        advice.append("Very hot weather. Carry plenty of water, sunscreen, and avoid riding during peak afternoon hours.")

    elif temperature >= 28:
        advice.append("Warm weather. Light cotton clothing is recommended.")

    elif temperature <= 10:
        advice.append("Cold weather. Wear layered clothing and be cautious of reduced visibility due to fog.")

    if weather_code in [61,63,65,80,81,82]:
        advice.append("Rain expected. Carry rain gear and waterproof luggage.")

    if weather_code in [95,96,99]:
        advice.append("Thunderstorms expected. Avoid long-distance riding if possible.")

    if wind_speed >= 25:
        advice.append("Strong winds expected. Ride cautiously, especially on highways.")
    
    if rain_probability >= 70:
        advice.append("High chance of rain. Consider rescheduling outdoor activities.")
    elif rain_probability >= 40:
        advice.append("Carry an umbrella or rain jacket.")

    if not advice:
        advice.append("Weather looks favorable for road travel.")

    return advice

@app.post("/calculate-budget")
def calculate_budget(request: BudgetRequest):

    # -----------------------
    # Fuel Cost
    # -----------------------
    mileage = VEHICLE_MILEAGE.get(request.vehicle_type.lower())

    if mileage is None:
        return {
            "error": "Invalid vehicle type. Use: bike, car_petrol or car_diesel."
        }

    liters_required = request.distance_km / mileage
    fuel_cost = round(liters_required * FUEL_PRICE)

    # -----------------------
    # Accommodation
    # -----------------------
    hotel_rate = HOTEL_RATES.get(request.budget_type.lower())

    if hotel_rate is None:
        return {
            "error": "Invalid budget type. Use: budget, mid or luxury."
        }

    rooms_required = ceil(request.travelers / 2)

    accommodation_cost = (
        hotel_rate
        * request.trip_days
        * rooms_required
    )

    # -----------------------
    # Food Cost
    # -----------------------
    food_cost = (
        FOOD_PER_PERSON
        * request.travelers
        * request.trip_days
    )

    # -----------------------
    # Activity Cost
    # -----------------------
    activity_rate = ACTIVITY_COST.get(request.activity_level.lower())

    if activity_rate is None:
        return {
            "error": "Invalid activity level. Use: low, medium or high."
        }

    activity_cost = (
        activity_rate
        * request.travelers
        * request.trip_days
    )

    # -----------------------
    # Miscellaneous
    # -----------------------
    miscellaneous_cost = (
        MISC_PER_PERSON
        * request.travelers
        * request.trip_days
    )

    # -----------------------
    # Subtotal
    # -----------------------
    subtotal = (
        fuel_cost
        + accommodation_cost
        + food_cost
        + activity_cost
        + miscellaneous_cost
    )

    # -----------------------
    # Emergency Buffer
    # -----------------------
    emergency_buffer = round(subtotal * 0.10)

    total_cost = subtotal + emergency_buffer
    # -----------------------
    # Budget Assessment
    # -----------------------

    daily_budget = round(total_cost / request.trip_days)
    cost_per_person = round(total_cost / request.travelers)    
    fuel_percentage = round((fuel_cost / total_cost) * 100)
    accommodation_percentage = round((accommodation_cost / total_cost) * 100)
    food_percentage = round((food_cost / total_cost) * 100)
    activity_percentage = round((activity_cost / total_cost) * 100)
    miscellaneous_percentage = round((miscellaneous_cost / total_cost) * 100)

    money_saving_tips = []

    if request.budget_type.lower() == "budget":
        money_saving_tips.extend([
            "Book accommodation in advance to secure better prices.",
            "Eat at highly rated local restaurants instead of tourist hotspots.",
            "Carry reusable water bottles and snacks.",
            "Group nearby attractions together to reduce fuel consumption."
        ])

    elif request.budget_type.lower() == "mid":
        money_saving_tips.extend([
            "Compare hotel prices before booking.",
            "Pre-book popular attractions online for discounts.",
            "Use digital payment offers whenever available."
        ])

    else:
        money_saving_tips.extend([
            "Reserve premium hotels well in advance.",
            "Keep a healthy emergency reserve for unexpected expenses.",
            "Consider travel insurance for long-distance trips."
        ])


    # -----------------------
    # Response
    # -----------------------
    return {
    "trip_summary": {
        "distance_km": request.distance_km,
        "trip_days": request.trip_days,
        "vehicle_type": request.vehicle_type,
        "travelers": request.travelers,
        "budget_type": request.budget_type,
        "activity_level": request.activity_level
    },

    "budget_breakdown": {
        "fuel_cost": fuel_cost,
        "fuel_percentage": fuel_percentage,

        "accommodation_cost": accommodation_cost,
        "accommodation_percentage": accommodation_percentage,

        "food_cost": food_cost,
        "food_percentage": food_percentage,

        "activity_cost": activity_cost,
        "activity_percentage": activity_percentage,

        "miscellaneous_cost": miscellaneous_cost,
        "miscellaneous_percentage": miscellaneous_percentage,

        "emergency_buffer": emergency_buffer,

        "total_cost": total_cost
    },

    "budget_assessment": {
        "estimated_total": total_cost,
        "daily_budget": daily_budget,
        "cost_per_person": cost_per_person,
        "travel_style": request.budget_type.capitalize()
    },

    "money_saving_tips": money_saving_tips
    }


class WeatherRequest(BaseModel):
    city: str





@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "RideBuddy Services API",
        "version": "1.0.0"
    }



@app.post("/weather")
def get_weather(request: WeatherRequest):

    # Step 1 - Find city coordinates
    geo_url = (
        f"https://geocoding-api.open-meteo.com/v1/search"
        f"?name={request.city}&count=1"
    )

    geo_response = requests.get(geo_url).json()

    if "results" not in geo_response:
        return {
            "error": "City not found."
        }

    location = geo_response["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # Step 2 - Get current weather
    weather_url = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    f"&current="
    f"temperature_2m,"
    f"relative_humidity_2m,"
    f"is_day,"
    f"weather_code,"
    f"wind_speed_10m"
    f"&daily=precipitation_probability_max"
    f"&forecast_days=1"
    f"&timezone=auto"
)

    weather_response = requests.get(weather_url).json()

    current = weather_response["current"]
    daily = weather_response["daily"]
    rain_probability = daily["precipitation_probability_max"][0]

    condition = WEATHER_CODES.get(
        current["weather_code"],
        "Unknown"
    )

    travel_advice = generate_travel_advice(
        current["temperature_2m"],
        current["weather_code"],
        current["wind_speed_10m"],
        rain_probability
    )

    return {
    "city": request.city,
    "current_weather": {
        "temperature_c": current["temperature_2m"],
        "condition": condition,
        "wind_speed_kmh": current["wind_speed_10m"],
        "humidity_percent": current["relative_humidity_2m"],
        "rain_probability_percent": rain_probability,
        "is_day": bool(current["is_day"])
    },
    "travel_advice": travel_advice
    }