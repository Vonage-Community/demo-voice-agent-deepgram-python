# Pug rescue lookup — hardcoded by zip prefix for demo reliability

# Keyed by the first digit of the zip code (broad US region)
# Each entry is a list of (name, city, state, phone) tuples


PUG_RESCUES_BY_REGION: dict[str, list[tuple[str, str, str, str]]] = {
    "0": [  # Northeast
        ("Pug Rescue of New England",    "Boston",       "MA", "617-555-0182"),
        ("NYC Pug Rescue",               "New York",     "NY", "212-555-0193"),
        ("Mid-Atlantic Pug Rescue",      "Philadelphia", "PA", "215-555-0147"),
    ],
    "1": [  # Northeast / Mid-Atlantic
        ("NYC Pug Rescue",               "New York",     "NY", "212-555-0193"),
        ("Mid-Atlantic Pug Rescue",      "Philadelphia", "PA", "215-555-0147"),
        ("Pug Rescue of New England",    "Boston",       "MA", "617-555-0182"),
    ],
    "2": [  # Southeast
        ("Carolina Pug Rescue",          "Charlotte",    "NC", "704-555-0138"),
        ("Virginia Pug Rescue",          "Richmond",     "VA", "804-555-0161"),
        ("Mid-Atlantic Pug Rescue",      "Baltimore",    "MD", "410-555-0174"),
    ],
    "3": [  # Southeast / Florida
        ("Florida Pug Rescue",           "Orlando",      "FL", "407-555-0129"),
        ("Georgia Pug Rescue",           "Atlanta",      "GA", "404-555-0156"),
        ("Carolina Pug Rescue",          "Charlotte",    "NC", "704-555-0138"),
    ],
    "4": [  # Midwest
        ("Great Lakes Pug Rescue",       "Chicago",      "IL", "312-555-0183"),
        ("Ohio Pug Rescue",              "Columbus",     "OH", "614-555-0117"),
        ("Michigan Pug Rescue",          "Detroit",      "MI", "313-555-0142"),
    ],
    "5": [  # Midwest / Plains
        ("Midwest Pug Rescue",           "Minneapolis",  "MN", "612-555-0196"),
        ("Great Plains Pug Rescue",      "Kansas City",  "MO", "816-555-0163"),
        ("Iowa Pug Rescue",              "Des Moines",   "IA", "515-555-0128"),
    ],
    "6": [  # Midwest / South
        ("Great Lakes Pug Rescue",       "Chicago",      "IL", "312-555-0183"),
        ("Heartland Pug Rescue",         "St. Louis",    "MO", "314-555-0177"),
        ("Nebraska Pug Rescue",          "Omaha",        "NE", "402-555-0144"),
    ],
    "7": [  # South / Texas
        ("Texas Pug Rescue",             "Dallas",       "TX", "214-555-0191"),
        ("Lone Star Pug Rescue",         "Houston",      "TX", "713-555-0158"),
        ("Oklahoma Pug Rescue",          "Oklahoma City","OK", "405-555-0135"),
    ],
    "8": [  # Mountain West
        ("Rocky Mountain Pug Rescue",    "Denver",       "CO", "303-555-0169"),
        ("Arizona Pug Rescue",           "Phoenix",      "AZ", "602-555-0184"),
        ("New Mexico Pug Rescue",        "Albuquerque",  "NM", "505-555-0122"),
    ],
    "9": [  # West Coast
        ("Southern California Pug Rescue","Los Angeles", "CA", "310-555-0175"),
        ("NorCal Pug Rescue",            "San Francisco","CA", "415-555-0148"),
        ("Pacific Northwest Pug Rescue", "Seattle",      "WA", "206-555-0131"),
    ],
}

DEFAULT_RESCUES = [
    ("National Pug Dog Club Rescue",     "Nationwide",   "US", "800-555-0100"),
    ("Pug Nation Rescue",                "Los Angeles",  "CA", "310-555-0175"),
    ("Mid-Atlantic Pug Rescue",          "Philadelphia", "PA", "215-555-0147"),
]