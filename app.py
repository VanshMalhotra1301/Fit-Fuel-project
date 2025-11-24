# app.py
from flask import Flask, render_template, request
from utils import validate_inputs, calculate_macros, get_meal_plan, safe_load_model

app = Flask(__name__)

# Load Model (Optional)
MODEL = safe_load_model("calorie_model.pkl")

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

    # BMR
    if gender.lower().startswith("m"):
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Activity
    activity_map = {
        "sedentary": 1.2, "light": 1.375, "moderate": 1.55,
        "active": 1.725, "very active": 1.9
    }
    # Match user string to map keys (approximate)
    act_key = str(data["activity"]).lower().split()[0] # basic matching
    if "sedentary" in str(data["activity"]).lower(): act_val = 1.2
    elif "light" in str(data["activity"]).lower(): act_val = 1.375
    elif "moderate" in str(data["activity"]).lower(): act_val = 1.55
    elif "very" in str(data["activity"]).lower(): act_val = 1.9
    elif "extra" in str(data["activity"]).lower(): act_val = 1.9
    else: act_val = 1.2

    tdee = int(bmr * act_val)

    # Goal
    goal = str(data["goal"]).lower()
    if "fat" in goal: tdee -= 300
    elif "muscle" in goal: tdee += 300
    
    tdee = max(1200, tdee)

    # Macros & Plan
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

    # --- FIX IS HERE: passing plan=meal_plan ---
    return render_template(
        "result.html",
        tdee=tdee,
        calories=tdee,
        macros=macros,
        plan=meal_plan,      # <--- CHANGED FROM meal_plan=meal_plan
        prediction=prediction,
        user_data=data
    )

if __name__ == "__main__":

    app.run(debug=True, port=5000)
