import requests
import json
import os
import time
import glob
import re
from datetime import datetime
import unicodedata
import asyncio
import nest_asyncio
import edge_tts
from indic_transliteration import sanscript
import ephem
import math

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Sanskrit Names Data
TITHI_NAMES = [
    "Amāvāsyā", "Pratipad", "Dvitīyā", "Tṛtīyā", "Caturthī", "Pañcamī", "Ṣaṣṭhī", 
    "Saptamī", "Aṣṭamī", "Navamī", "Daśamī", "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī", "Pūrṇimā"
]

NAKSHATRA_NAMES = [
    "Aśvinī", "Bharaṇī", "Kṛttikā", "Rohiṇī", "Mṛgaśīrṣā", "Ārdrā", "Punarvasu", "Puṣya", "Āśleṣā",
    "Maghā", "Pūrvaphalgunī", "Uttaraphalgunī", "Hasta", "Citrā", "Svātī", "Viśākhā", "Anurādhā",
    "Jyeṣṭhā", "Mūla", "Pūrvāṣāḍhā", "Uttarāṣāḍhā", "Śravaṇa", "Dhaniṣṭhā", "Śatabhiṣak",
    "Pūrvabhādrapadā", "Uttarabhādrapadā", "Revatī"
]

MASA_NAMES = [
    "Caitra", "Vaiśākha", "Jyeṣṭha", "Āṣāḍha", "Śrāvaṇa", "Bhādrapada", 
    "Āśvina", "Kārttika", "Mārgaśīrṣa", "Pauṣa", "Māgha", "Phālguna"
]

from datetime import datetime, timedelta

def get_accurate_panchanga_local(latitude, longitude, timezone, year, month, day):
    """
    Calculates accurate Panchanga elements using pyephem (high precision).
    """
    try:
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)
        
        # Calculate start time for sunrise search (Local Midnight converted to UTC)
        # We want the sunrise of the given calendar date.
        # So start searching from slightly before local sunrise (e.g., local midnight - safety buffer).
        # Actually, just using Local Midnight UTC is safe because sunrise is after midnight.
        # Local Midnight = year/month/day 00:00:00
        # UTC = Local - TimezoneOffset
        
        local_midnight = datetime(year, month, day)
        # Handle timezone subtraction manually or using timedelta
        # Timezone is float hours (e.g. -6.0)
        start_utc = local_midnight - timedelta(hours=timezone)
        
        # Set observer date to start search (minus 1 hour buffer to be safe)
        observer.date = start_utc - timedelta(hours=1)
        
        sun = ephem.Sun()
        try:
            sunrise = observer.next_rising(sun)
            observer.date = sunrise
        except:
            # Fallback to noon local time if sunrise calc fails
            noon_utc = local_midnight + timedelta(hours=12) - timedelta(hours=timezone)
            observer.date = noon_utc

        sun = ephem.Sun(observer)
        moon = ephem.Moon(observer)
        
        # Get Ecliptic Coordinates (Geocentric)
        sun_ecl = ephem.Ecliptic(sun)
        moon_ecl = ephem.Ecliptic(moon)
        
        # Ayanamsa (Lahiri) approximation for 2000-2050
        # Ayanamsa ~ 23.85 + 0.0139 * (Year - 2000)
        # More precise: 23deg 51min roughly for now.
        # Using a simple linear model for recent times.
        t_century = (ephem.julian_date(observer.date) - 2451545.0) / 36525.0
        ayanamsa_deg = 23.85 + 1.4 * t_century # Rough approximation
        # Better: use fixed value 24.2 for 2025.
        ayanamsa_rad = math.radians(ayanamsa_deg)

        # 1. Tithi (Independent of Ayanamsa)
        # Difference between Moon and Sun longitudes
        diff = (moon_ecl.lon - sun_ecl.lon) % (2 * math.pi)
        tithi_num = math.ceil(math.degrees(diff) / 12.0)
        
        # Determine Paksha and Tithi Name
        if tithi_num <= 15:
            paksha = "Śukla Pakṣe"
            tithi_name = TITHI_NAMES[tithi_num] if tithi_num < 15 else "Pūrṇimā"
        else:
            paksha = "Kṛṣṇa Pakṣe"
            idx = tithi_num - 15
            tithi_name = TITHI_NAMES[idx] if idx < 15 else "Amāvāsyā"
            
        # 2. Nakshatra (Needs Ayanamsa)
        # Nirayana Longitude = Sayana - Ayanamsa
        nirayana_moon = (moon_ecl.lon - ayanamsa_rad) % (2 * math.pi)
        nakshatra_num = math.ceil(math.degrees(nirayana_moon) * 27 / 360.0)
        if nakshatra_num == 0: nakshatra_num = 27
        nakshatra_name = NAKSHATRA_NAMES[int(nakshatra_num) - 1]
        
        # 3. Masa (Lunar Month)
        # Based on Solar Rashi (Nirayana Sun)
        nirayana_sun = (sun_ecl.lon - ayanamsa_rad) % (2 * math.pi)
        solar_rashi = int(math.degrees(nirayana_sun) / 30.0) # 0 = Mesha
        
        # Amanta Rule: Lunar Month = Solar Rashi + 1 (Index 0-11)
        # If Solar Rashi is Dhanu (8), Month is Pausha (9)
        masa_idx = (solar_rashi + 1) % 12
        masa_name = MASA_NAMES[masa_idx]
        
        return {
            "tithi": tithi_name,
            "paksha": paksha,
            "nakshatra": nakshatra_name,
            "masa": masa_name
        }
    except Exception as e:
        print(f"Error in local calculation: {e}")
        return None

def cleanup_old_audio_files(directory=".", pattern="sankalpam_*.mp3", max_age_seconds=86400):
    """
    Deletes files matching the pattern that are older than max_age_seconds.
    Default: 24 hours (86400 seconds).
    """
    now = time.time()
    for filepath in glob.glob(os.path.join(directory, pattern)):
        try:
            file_age = now - os.path.getmtime(filepath)
            if file_age > max_age_seconds:
                os.remove(filepath)
        except Exception as e:
            pass # Ignore errors during cleanup

def get_panchanga(latitude, longitude, timezone, year=None, month=None, day=None, location_name="Unknown"):
    """
    Get the Hindu Panchanga details for a specific location and date.
    
    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        timezone (float): Timezone offset from UTC (e.g., -6.0 for CST).
        year (int, optional): Year (default: current year).
        month (int, optional): Month (default: current month).
        day (int, optional): Day (default: current day).
        location_name (str, optional): Name of the location (default: "Unknown").
        
    Returns:
        dict: A dictionary containing the Panchanga details.
    """
    # Use current date if not provided
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    if day is None:
        day = now.day

    # API Configuration
    base_url = os.getenv("PANCHANGAM_API_URL", "http://localhost:8080/api/panchanga")
    
    params = {
        "year": year,
        "month": month,
        "day": day,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "locationName": location_name
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_sankalpam(latitude, longitude, timezone, year=None, month=None, day=None, location_name="Unknown"):
    """
    Generates a Sankalpam string for a specific location and date.
    """
    # 1. Get Panchanga Data
    data = get_panchanga(latitude, longitude, timezone, year, month, day, location_name)
    
    if "error" in data:
        return f"Error fetching Panchanga data: {data['error']}"

    # 2. Extract Components
    try:
        samvatsara = data['samvatsara']['name']
        ritu = data['ritu']['name']
        masa = data['masa']['name']
        tithi_full = data['tithi']['name']
        vara = data['vara']['name']
        nakshatra = data['nakshatra']['name']
        
        # 3. Derive Ayana (Approximation based on date)
        # Uttarayana: Approx Jan 14 to July 16
        # Dakshinayana: Approx July 16 to Jan 14
        # Using the date from the response or input
        d_year = data['date']['year']
        d_month = data['date']['month']
        d_day = data['date']['day']
        
        # Override with Accurate Local Calculation (using pyephem)
        # This fixes discrepancies in Tithi/Nakshatra due to simplified C# model
        accurate_data = get_accurate_panchanga_local(latitude, longitude, timezone, d_year, d_month, d_day)
        if accurate_data:
            # Override if successful
            tithi_name = accurate_data['tithi']
            nakshatra = accurate_data['nakshatra']
            masa = accurate_data['masa']
            paksha = accurate_data['paksha']
            
            # Note: samvatsara is taken from API (which is fixed to use Saka year)
            # ritu is taken from API (usually fine based on month)
            # vara is taken from API (simple calculation)
        else:
            # Fallback to API data parsing
            # 4. Parse Paksha and Tithi
            # Normalize string to handle different unicode representations
            tithi_normalized = unicodedata.normalize('NFD', tithi_full)
            
            if "ukla" in tithi_full or "Śukla" in tithi_full or "Sukla" in tithi_full or "ukla" in tithi_normalized:
                paksha = "Śukla Pakṣe"
            elif "ṛṣṇa" in tithi_full or "rishna" in tithi_full or "Krishna" in tithi_full:
                paksha = "Kṛṣṇa Pakṣe"
            else:
                paksha = "Pakṣe" # Fallback

            # Clean Tithi name (remove paksha part if needed, but usually kept in Sankalpa)
            tithi_parts = tithi_full.split(' ')
            if len(tithi_parts) > 2:
                tithi_name = tithi_parts[-1] 
            else:
                tithi_name = tithi_full

        # Simple logic for Ayana: 
        # Jan 15 - July 15 -> Uttarayana
        # July 16 - Jan 14 -> Dakshinayana
        date_val = d_month * 100 + d_day
        if 115 <= date_val <= 715:
            ayana = "Uttarāyaṇe"
        else:
            ayana = "Dakṣiṇāyane"

        # 5. Construct Sankalpam
        sankalpam = (
            f"Śrī Śubha {samvatsara} Nāma Samvatsare, {ayana}, {ritu} Ṛtau, "
            f"{masa} Māse, {paksha}, {tithi_name} Śubha Tithau, "
            f"{vara} Vāsara Yuktāyām, {nakshatra} Nakṣatra Yuktāyām, "
            f"Śubha Yoga Śubha Karaṇa Evaṃ Guṇa Viśeṣaṇa Viśiṣṭāyām, "
            f"Asyāṃ Śubha Tithau..."
        )
        
        return {
            "sankalpam": sankalpam,
            "components": {
                "samvatsara": samvatsara,
                "ayana": ayana,
                "ritu": ritu,
                "masa": masa,
                "paksha": paksha,
                "tithi": tithi_name,
                "vara": vara,
                "nakshatra": nakshatra
            }
        }

    except KeyError as e:
        return {"error": f"Error parsing Panchanga data: Missing key {e}"}

async def _generate_audio(text, output_file, voice="hi-IN-SwaraNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def get_sankalpam_voice(latitude, longitude, timezone, year=None, month=None, day=None, location_name="Unknown"):
    """
    Generates a Sankalpam audio file for a specific location and date.
    
    Returns:
        dict: Contains the path to the generated audio file and the text.
    """
    # 0. Cleanup old files
    cleanup_old_audio_files()

    # 1. Get Sankalpam Text
    result = get_sankalpam(latitude, longitude, timezone, year, month, day, location_name)
    
    if isinstance(result, str): # Error case (legacy string return)
         return {"error": result}
    if "error" in result:
        return result
        
    sankalpam_iast = result["sankalpam"]
    
    # 2. Transliterate IAST to Devanagari
    # Edge TTS (Hindi voices) reads Devanagari much better than IAST
    try:
        sankalpam_devanagari = sanscript.transliterate(sankalpam_iast, sanscript.IAST, sanscript.DEVANAGARI)
    except Exception as e:
        return {"error": f"Transliteration failed: {str(e)}"}

    # 3. Generate Audio with Unique Filename
    # Sanitize location name
    safe_location = re.sub(r'[^a-zA-Z0-9]', '_', location_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"sankalpam_{safe_location}_{timestamp}.mp3"

    try:
        asyncio.run(_generate_audio(sankalpam_devanagari, output_file))
    except Exception as e:
        return {"error": f"Audio generation failed: {str(e)}"}
        
    return {
        "audio_file": output_file,
        "sankalpam_text": sankalpam_iast,
        "sankalpam_devanagari": sankalpam_devanagari
    }

if __name__ == "__main__":
    # Test the function with Frisco, TX coordinates
    print("\n--- Sankalpam Voice ---")
    voice_result = get_sankalpam_voice(
        latitude=33.1507, 
        longitude=-96.8236, 
        timezone=-6.0, 
        location_name="Frisco, TX"
    )
    print(json.dumps(voice_result, indent=2, ensure_ascii=False))
