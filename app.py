# app.py
from flask import Flask, render_template, request, send_from_directory
from utils import validate_inputs, calculate_macros, get_meal_plan, safe_load_model
import os

# Flask must know your templates are in ROOT
app = Flask(__name__, template_folder='.', static_folder='.')

# Load Model (Optional)
MODEL = safe_load_model("calorie_model.pkl")


# ---------------------------
# SERVE ROOT CSS & JS FILES
# ---------------------------

@app.route('/style.css')
def serve_css():
    return send_from_directory(os.path.dirname(__file__), "style.css")

@app.route('/app.js')
def serve_js():
    return send_from_directory(os.path.dirname(__file__), "app.js")


# ---------------------------
# ROUTES
# ---------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    form = request.form
    data, errors = validate_inputs(form)

    if errors:
        return render_template("index.html", errors=errors, old=form)

    # Inputs
    weight = data["weight"]
    height = data["height"]
    age = data["age"]
    gender = data["gender"]

    # BMR (Mifflin–St Jeor)
    if gender.lower().startswith("m"):
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Activity Levels
    activity = str(data["activity"]).lower()
    if "sedentary" in activity: act_val = 1.2
    elif "light" in activity: act_val = 1.375
    elif "moderate" in activity: act_val = 1.55
    elif "very" in activity: act_val = 1.725
    elif "extra" in activity: act_val = 1.9
    else: act_val = 1.2

    tdee = int(bmr * act_val)

    # Goal adjust
    goal = str(data["goal"]).lower()
    if "fat" in goal:
        tdee -= 300
    elif "muscle" in goal:
        tdee += 300

    tdee = max(1200, tdee)

    # Macros and Meal Plan
    macros = calculate_macros(tdee, goal=goal)
    meal_plan = get_meal_plan(tdee, diet_pref=data["diet"], goal=goal)

    # ML Prediction
    prediction = None
    if MODEL:
        try:
            features = [[weight, height, age, 1 if gender.lower().startswith("m") else 0]]
            prediction = MODEL.predict(features)[0]
        except:
            prediction = None

    return render_template(
        "result.html",
        tdee=tdee,
        calories=tdee,
        macros=macros,
        plan=meal_plan,
        prediction=prediction,
        user_data=data
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
