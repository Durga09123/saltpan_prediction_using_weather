import streamlit as st
import pandas as pd
import joblib
import requests
import base64


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Saltpan Suitability Prediction",
    page_icon="🌤️",
    layout="centered"
)


# =========================================================
# BACKGROUND IMAGE
# =========================================================

def set_background(image_file):

    with open(image_file, "rb") as file:

        encoded_image = base64.b64encode(
            file.read()
        ).decode()

    css = f"""
<style>

.stApp {{
    background-image:
    linear-gradient(
        rgba(100, 248, 255, 0.50),
        rgba(100, 220, 255, 0.50)
    ),
    url("data:image/jpg;base64,{encoded_image}");

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}


/* Main headings */
h1, h3, h4, h5, h6 {{
    color: #06283D !important;
}}


/* Normal text */
p, span, label {{
    color: #06283D !important;
}}


/* Selectbox text */
div[data-baseweb="select"] {{
    color: #FFFFFF !important;
}}

div[data-baseweb="select"] * {{
    color: #FFFFFF !important;
}}


/* Number input text */
.stNumberInput input {{
    color: #FFFFFF !important;
}}


/* Number input labels */
.stNumberInput label {{
    color: #FFFFFF !important;
}}


/* Buttons */

.stButton button {{
    color: #FFFFFF !important;
    font-weight: 600;
    transition: all 0.3s ease;
}}

.stButton button p {{
    color: #FFFFFF !important;
}}

.stButton button span {{
    color: #FFFFFF !important;
}}

/* Hover Effect */

.stButton button:hover {{
    background-color: #0077B6 !important;
    color: #FFFFFF !important;
    transform: scale(1.03);
}}

.stButton button:hover p {{
    color: #FFFFFF !important;
}}

.stButton button:hover span {{
    color: #FFFFFF !important;
}}

/* Info / success / error text */
div[data-testid="stAlert"] {{
    color: #FFFFFF !important;
}}

</style>
"""

    st.markdown(
        css,
        unsafe_allow_html=True
    )


# Set background image
set_background("saltpan_background.jpg")


# =========================================================
# TITLE
# =========================================================

st.title(
    "🌤️ AI-Based Saltpan Suitability Prediction"
)

st.write(
    "Select a saltpan location, get today's weather data, "
    "and predict whether the weather is suitable for "
    "salt manufacturing."
)


# =========================================================
# LOAD RANDOM FOREST MODEL
# =========================================================

@st.cache_resource
def load_model():

    return joblib.load(
        "saltpan_random_forest.pkl"
    )


model = load_model()


# =========================================================
# LOCATIONS
# =========================================================

LOCATIONS = {

    "Thoothukudi Coastal Area": {
        "latitude": 8.7522,
        "longitude": 78.1293
    },

    "Thoothukudi": {
        "latitude": 8.8225,
        "longitude": 78.1191
    },

    "Tharuvaikulam Coastal Area": {
        "latitude": 8.8928,
        "longitude": 78.1088
    },

    "Vellapatti Coastal Area": {
        "latitude": 8.9631,
        "longitude": 78.1763
    },

    "Vembar": {
        "latitude": 9.1037,
        "longitude": 78.3896
    },

    "Thoothukudi District Coastal Area": {
        "latitude": 9.0334,
        "longitude": 78.2439
    },

    "Kayalpattinam Coastal Area": {
        "latitude": 8.5413,
        "longitude": 78.0826
    }
}


# =========================================================
# GET TODAY'S WEATHER
# =========================================================

def get_today_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": [
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "wind_speed_10m_max",
            "precipitation_sum"
        ],


        "timezone": "Asia/Kolkata",

        "forecast_days": 1,

        "wind_speed_unit": "ms"
    }


    response = requests.get(
        url,
        params=params,
        timeout=15
    )


    response.raise_for_status()


    data = response.json()


    weather = {

        "date":
            data["daily"]["time"][0],

        "temperature":
            data["daily"]["temperature_2m_mean"][0],

        "humidity":
            data["daily"]["relative_humidity_2m_mean"][0],

        "wind":
            data["daily"]["wind_speed_10m_max"][0],

        "rainfall":
            data["daily"]["precipitation_sum"][0]
    }


    return weather


# =========================================================
# SESSION STATE
# =========================================================

# Weather values start at 0

if "temperature" not in st.session_state:

    st.session_state.temperature = 0.0


if "humidity" not in st.session_state:

    st.session_state.humidity = 0.0


if "wind" not in st.session_state:

    st.session_state.wind = 0.0


if "rainfall" not in st.session_state:

    st.session_state.rainfall = 0.0


if "weather_loaded" not in st.session_state:

    st.session_state.weather_loaded = False


if "weather_date" not in st.session_state:

    st.session_state.weather_date = ""


# =========================================================
# LOCATION SELECTION
# =========================================================

st.subheader("📍 Select Location")


selected_place = st.selectbox(

    "Choose a saltpan location:",

    list(LOCATIONS.keys())
)


selected_location = LOCATIONS[selected_place]


# =========================================================
# DISPLAY PLACE, LATITUDE AND LONGITUDE
# =========================================================

st.info(
    f"""
**Place:** {selected_place}

**Latitude:** {selected_location["latitude"]}

**Longitude:** {selected_location["longitude"]}
"""
)


# =========================================================
# GET WEATHER BUTTON
# =========================================================

if st.button(
    "🌦️ Get Today's Weather",
    use_container_width=True
):

    try:

        with st.spinner(
            "Fetching today's weather data..."
        ):

            weather = get_today_weather(

                selected_location["latitude"],

                selected_location["longitude"]
            )


        # -----------------------------------------------
        # UPDATE WEATHER INPUT VALUES
        # -----------------------------------------------

        st.session_state.temperature = float(

            weather["temperature"]
        )


        st.session_state.humidity = float(

            weather["humidity"]
        )


        st.session_state.wind = float(

            weather["wind"]
        )


        st.session_state.rainfall = float(

            weather["rainfall"]
        )


        st.session_state.weather_date = (

            weather["date"]
        )


        st.session_state.weather_loaded = True


        st.success(
            "✅ Today's weather data fetched successfully!"
        )


    except Exception as e:

        st.error(
            f"❌ Unable to fetch weather data: {e}"
        )


# =========================================================
# WEATHER INPUTS
# =========================================================

st.subheader("🌦️ Weather Data")


col1, col2 = st.columns(2)


with col1:

    st.number_input(

        "Temperature (°C)",

        min_value=0.0,

        format="%.2f",

        key="temperature"
    )


    st.number_input(

        "Humidity (%)",

        min_value=0.0,

        format="%.2f",

        key="humidity"
    )


with col2:

    st.number_input(

        "Maximum Wind Speed (m/s)",

        min_value=0.0,

        format="%.2f",

        key="wind"
    )


    st.number_input(

        "Rainfall (mm)",

        min_value=0.0,

        format="%.2f",

        key="rainfall"
    )


# =========================================================
# WEATHER DATE
# =========================================================

if st.session_state.weather_loaded:

    st.caption(
        f"Weather date: {st.session_state.weather_date}"
    )


# =========================================================
# PREDICTION
# =========================================================

st.subheader(" Prediction")


if st.button(

    "Predict Suitability",

    use_container_width=True
):

    # -----------------------------------------------------
    # MODEL INPUT
    #
    # IMPORTANT:
    # These column names MUST exactly match the
    # columns used during model training.
    # -----------------------------------------------------

    new_weather = pd.DataFrame({

        "Temperature (°C)": [

            st.session_state.temperature
        ],

        "Humidity (%)": [

            st.session_state.humidity
        ],

        "Wind_Speed  (m/s)": [

            st.session_state.wind
        ],

        "Precipitation_Sum (mm)": [

            st.session_state.rainfall
        ]
    })


    # -----------------------------------------------------
    # PREDICT CLASS
    # -----------------------------------------------------

    prediction = model.predict(

        new_weather
    )


    # -----------------------------------------------------
    # PREDICTION PROBABILITY
    # -----------------------------------------------------

    probability = model.predict_proba(

        new_weather
    )


    predicted_class = int(

        prediction[0]
    )


    predicted_probability = (

        probability[0][predicted_class] * 100
    )


    # -----------------------------------------------------
    # DISPLAY RESULT
    # -----------------------------------------------------

    if predicted_class == 1:

        st.success(
            "✅ Suitable for Salt Manufacturing"
        )

    else:

        st.error(
            "❌ Not Suitable for Salt Manufacturing"
        )


    # -----------------------------------------------------
    # ONLY PROBABILITY
    # -----------------------------------------------------

    st.metric(

        "Prediction Probability",

        f"{predicted_probability:.2f}%"
    )

