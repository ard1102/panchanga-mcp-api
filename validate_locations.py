import json
from datetime import datetime
from panchanga_tool import get_sankalpam

# Configuration
DATE_STR = "2025-12-23"  # Testing for Dec 23, 2025
YEAR, MONTH, DAY = 2025, 12, 23

# Locations: Name, Lat, Lon, Timezone
LOCATIONS = [
    ("Frisco, TX", 33.1507, -96.8236, -6.0),
    ("New York, NY", 40.7128, -74.0060, -5.0),
    ("London, UK", 51.5074, -0.1278, 0.0),
    ("Mumbai, India", 19.0760, 72.8777, 5.5),
    ("Sydney, Australia", -33.8688, 151.2093, 11.0),
    ("Tokyo, Japan", 35.6762, 139.6503, 9.0),
    ("Dubai, UAE", 25.2048, 55.2708, 4.0),
    ("San Francisco, CA", 37.7749, -122.4194, -8.0),
    ("Singapore", 1.3521, 103.8198, 8.0),
    ("Berlin, Germany", 52.5200, 13.4050, 1.0)
]

def test_location(name, lat, lon, tz):
    print(f"\nTesting {name}...")
    
    try:
        # Call the tool function directly
        result = get_sankalpam(lat, lon, tz, YEAR, MONTH, DAY, name)
        
        if isinstance(result, dict) and "sankalpam" in result:
            text = result["sankalpam"]
            print(f"Sankalpam Text (First 100 chars): {text[:100]}...")
            
            # Check for Samvatsara name in text
            if "Viśvāvasu" in text or "Viswavasu" in text:
                print("✅ Samvatsara: Viśvāvasu (Correct)")
            elif "Raudra" in text:
                print("❌ Samvatsara: Raudra (Incorrect)")
            else:
                # Extract actual samvatsara from text if possible
                print(f"⚠️ Samvatsara: Unknown/Not found in text snippet")
                
            # Print components for verification
            comps = result.get("components", {})
            print(f"   Masa: {comps.get('masa')}")
            print(f"   Tithi: {comps.get('tithi')}") # Note: 'tithi' key might not exist in components dict in get_sankalpam?
            # get_sankalpam returns "masa", "paksha" in components.
            # Tithi name is embedded in Sankalpam string but not in components dict explicitly as 'tithi' name?
            # Let's check the code. Line 144: "masa", "paksha" are there.
            
            return result
        else:
            print(f"❌ Error: {result}")
            return None

    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

if __name__ == "__main__":
    print(f"Starting validation for date: {DATE_STR}")
    results = {}
    for loc in LOCATIONS:
        res = test_location(*loc)
        if res:
            results[loc[0]] = res
            
    # Save full results
    with open("validation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nValidation complete. Results saved to validation_results.json")
