import os
import math
import joblib
import random
import pandas as pd
from functools import lru_cache
from datasets import load_dataset

# ----------------------------------------------------------------------
# 1. ADVANCED CURATED MEAL DATABASE (Updated with Macros)
# ----------------------------------------------------------------------
# Added keys: 'p' (protein), 'c' (carbs), 'f' (fats) per serving
CURATED_DB = {
    "veg": {
        "Breakfast": [
            {"name": "Paneer Bhurji & Toast", "calories": 350, "p": 18, "c": 30, "f": 16},
            {"name": "Masala Oats with Veggies", "calories": 300, "p": 10, "c": 45, "f": 8},
            {"name": "Vegetable Poha with Peanuts", "calories": 320, "p": 8, "c": 50, "f": 10},
            {"name": "Greek Yogurt Parfait with Berries", "calories": 280, "p": 15, "c": 35, "f": 6},
            {"name": "Besan Chilla (Gram Flour Pancakes)", "calories": 250, "p": 12, "c": 30, "f": 8},
            {"name": "Avocado Toast with Chili Flakes", "calories": 350, "p": 9, "c": 40, "f": 18},
            {"name": "Idli Sambar (3 pcs)", "calories": 300, "p": 12, "c": 55, "f": 4},
            {"name": "Aloo Paratha with Curd", "calories": 450, "p": 10, "c": 65, "f": 18},
        ],
        "Lunch": [
            {"name": "Paneer Butter Masala & 2 Roti", "calories": 550, "p": 22, "c": 50, "f": 30},
            {"name": "Dal Tadka with Jeera Rice", "calories": 450, "p": 18, "c": 70, "f": 12},
            {"name": "Grilled Vegetable Quinoa Salad", "calories": 400, "p": 14, "c": 55, "f": 12},
            {"name": "Rajma Chawal Bowl", "calories": 500, "p": 18, "c": 80, "f": 10},
            {"name": "Palak Paneer with Brown Rice", "calories": 480, "p": 20, "c": 50, "f": 24},
            {"name": "Vegetable Biryani with Raita", "calories": 550, "p": 14, "c": 85, "f": 18},
            {"name": "Chickpea (Chole) Curry & Rice", "calories": 520, "p": 16, "c": 80, "f": 14},
        ],
        "Dinner": [
            {"name": "Mixed Vegetable Soup & Salad", "calories": 300, "p": 8, "c": 40, "f": 10},
            {"name": "Roti with Baingan Bharta", "calories": 350, "p": 10, "c": 55, "f": 10},
            {"name": "Stir-fry Tofu & Broccoli", "calories": 380, "p": 25, "c": 20, "f": 22},
            {"name": "Lentil Soup (Dal) & 1 Roti", "calories": 320, "p": 14, "c": 50, "f": 6},
            {"name": "Khichdi with Ghee", "calories": 350, "p": 10, "c": 55, "f": 12},
            {"name": "Grilled Mushroom Wrap", "calories": 340, "p": 12, "c": 45, "f": 12},
        ],
        "Snacks": [
            {"name": "Roasted Makhana (Fox Nuts)", "calories": 100, "p": 3, "c": 20, "f": 1},
            {"name": "Fruit Salad Bowl", "calories": 120, "p": 2, "c": 28, "f": 0},
            {"name": "Handful of Almonds & Walnuts", "calories": 180, "p": 6, "c": 6, "f": 16},
            {"name": "Carrot & Cucumber Sticks with Hummus", "calories": 150, "p": 6, "c": 15, "f": 8},
        ]
    },
    "non-veg": {
        "Breakfast": [
            {"name": "Scrambled Eggs (3 eggs) & Toast", "calories": 400, "p": 24, "c": 25, "f": 22},
            {"name": "Chicken Sausage Omelette", "calories": 450, "p": 30, "c": 5, "f": 32},
            {"name": "Boiled Eggs & Fruit Bowl", "calories": 300, "p": 18, "c": 25, "f": 14},
            {"name": "Turkey Bacon & Avocado Wrap", "calories": 420, "p": 25, "c": 30, "f": 22},
        ],
        "Lunch": [
            {"name": "Grilled Chicken Breast & Brown Rice", "calories": 500, "p": 45, "c": 50, "f": 10},
            {"name": "Chicken Curry & 2 Roti", "calories": 550, "p": 35, "c": 50, "f": 22},
            {"name": "Fish Curry with Steamed Rice", "calories": 480, "p": 30, "c": 60, "f": 15},
            {"name": "Chicken Burrito Bowl", "calories": 580, "p": 40, "c": 65, "f": 18},
        ],
        "Dinner": [
            {"name": "Grilled Salmon with Asparagus", "calories": 450, "p": 35, "c": 10, "f": 28},
            {"name": "Chicken Clear Soup & Salad", "calories": 300, "p": 25, "c": 15, "f": 12},
            {"name": "Mutton Rogan Josh (Light) & Roti", "calories": 550, "p": 30, "c": 40, "f": 30},
        ],
        "Snacks": [
            {"name": "Boiled Egg Whites (3)", "calories": 50, "p": 11, "c": 1, "f": 0},
            {"name": "Chicken Salami Roll-ups", "calories": 150, "p": 18, "c": 2, "f": 8},
            {"name": "Protein Shake (Whey)", "calories": 120, "p": 25, "c": 3, "f": 1},
        ]
    },
    "vegan": {
        "Breakfast": [
            {"name": "Tofu Scramble with Spinach", "calories": 300, "p": 20, "c": 15, "f": 18},
            {"name": "Oatmeal made with Almond Milk", "calories": 350, "p": 8, "c": 60, "f": 8},
            {"name": "Peanut Butter Banana Toast", "calories": 400, "p": 12, "c": 55, "f": 16},
        ],
        "Lunch": [
            {"name": "Chickpea Buddha Bowl", "calories": 500, "p": 18, "c": 75, "f": 14},
            {"name": "Lentil Curry (Dal) & Rice", "calories": 450, "p": 16, "c": 80, "f": 6},
            {"name": "Soya Chunk Pulao", "calories": 480, "p": 25, "c": 60, "f": 12},
        ],
        "Dinner": [
            {"name": "Quinoa Salad with Black Beans", "calories": 400, "p": 15, "c": 65, "f": 8},
            {"name": "Stir-fried Veggies with Cashews", "calories": 350, "p": 8, "c": 30, "f": 22},
        ],
        "Snacks": [
            {"name": "Apple Slices with Peanut Butter", "calories": 200, "p": 6, "c": 22, "f": 10},
            {"name": "Roasted Chickpeas", "calories": 150, "p": 7, "c": 20, "f": 5},
        ]
    }
}

# ----------------------------------------------------------------------
# 2. MODEL LOADER
# ----------------------------------------------------------------------
def safe_load_model(path="models/calorie_model.pkl"):
    if not os.path.exists(path):
        print(f"⚠️  Model not found at {path}. Skipping ML prediction.")
        return None
    try:
        model = joblib.load(path)
        print("✅ ML model loaded successfully.")
        return model
    except Exception as e:
        print(f"❌ Failed to load ML model: {e}")
        return None

# ----------------------------------------------------------------------
# 3. DATASET LOADER (UPDATED FOR MACROS)
# ----------------------------------------------------------------------
@lru_cache(maxsize=1)
def load_food_dataframe():
    dataset_name = "adarshzolekar/foods-nutrition-dataset"
    try:
        print("⏳ Loading food dataset...")
        ds = load_dataset(dataset_name)
        df = pd.DataFrame(ds["train"])

        # Normalize columns
        df.columns = [c.lower().strip() for c in df.columns]
        
        # Name handling
        possible_names = ['name', 'food_name', 'item', 'description', 'shrt_desc', 'desc']
        found_col = None
        for candidate in possible_names:
            if candidate in df.columns:
                found_col = candidate
                break
        
        if found_col:
            df.rename(columns={found_col: "food"}, inplace=True)
        elif "food" not in df.columns:
            for col in df.columns:
                if df[col].dtype == 'object':
                    df.rename(columns={col: "food"}, inplace=True)
                    break

        # Standardize Calories
        if "calories" in df.columns:
            df["calories"] = pd.to_numeric(df["calories"], errors="coerce").fillna(0)
        
        # --- NEW: Try to standardize Macros if columns exist ---
        # Look for protein, carb, fat columns and standardize them to p, c, f
        for col in df.columns:
            if "prot" in col: df.rename(columns={col: "p"}, inplace=True)
            if "carb" in col: df.rename(columns={col: "c"}, inplace=True)
            if "fat" in col and "sat" not in col: df.rename(columns={col: "f"}, inplace=True) # Avoid saturated fat

        # Ensure columns exist, fill with 0 if missing
        for macro in ['p', 'c', 'f']:
            if macro not in df.columns:
                df[macro] = 0.0
            else:
                df[macro] = pd.to_numeric(df[macro], errors="coerce").fillna(0)

        # Create is_veg
        if "is_veg" not in df.columns:
            nonveg_keywords = "chicken|egg|fish|mutton|beef|pork|shrimp|prawn|salmon|tuna|bacon|ham|sausage"
            try:
                df["is_veg"] = ~df["food"].str.contains(nonveg_keywords, case=False, na=False)
                df["is_veg"] = df["is_veg"].astype(int)
            except:
                df["is_veg"] = 1 

        print("✅ Food dataset loaded.")
        return df
    except Exception as e:
        print(f"❌ Could not load HF dataset: {e}")
        return None

# ----------------------------------------------------------------------
# 4. MACROS CALCULATION (TARGETS)
# ----------------------------------------------------------------------
def calculate_macros(total_calories, goal="maintenance"):
    goal = goal.lower()
    splits = {
        "fat loss":    (0.35, 0.35, 0.30), # High protein
        "muscle gain": (0.30, 0.45, 0.25),
        "maintenance": (0.20, 0.50, 0.30), # Adjusted maintenance to be more realistic standard
    }
    p_pct, c_pct, f_pct = splits.get(goal, splits["maintenance"])
    return {
        "protein_g": round(total_calories * p_pct / 4, 1),
        "carbs_g":   round(total_calories * c_pct / 4, 1),
        "fat_g":     round(total_calories * f_pct / 9, 1),
    }

# ----------------------------------------------------------------------
# 5. MEAL PLAN GENERATOR (UPDATED TO CALCULATE MEAL MACROS)
# ----------------------------------------------------------------------
def pick_from_curated(diet_pref, meal_type, target_kcal):
    """
    Picks a meal and SCALES the protein/carbs/fats based on calories.
    """
    diet_key = "veg"
    if "non" in diet_pref.lower(): diet_key = "non-veg"
    elif "vegan" in diet_pref.lower(): diet_key = "vegan"
    
    options = CURATED_DB.get(diet_key, {}).get(meal_type, [])
    
    # Fallback if list empty
    if not options:
        return {
            "name": "Healthy Choice", 
            "calories": target_kcal, 
            "protein": int(target_kcal * 0.2 / 4), # Estimate
            "carbs": int(target_kcal * 0.5 / 4),
            "fats": int(target_kcal * 0.3 / 9),
            "portion": "1 serving"
        }

    choice = random.choice(options)
    
    # Calculate Ratio to scale the portion
    # If target is 600 and food is 300, ratio is 2.0 (2 servings)
    ratio = target_kcal / choice["calories"]
    
    # Determine Portion Text
    if 0.8 <= ratio <= 1.2:
        portion = "1 Serving"
        display_ratio = 1.0
    elif ratio > 1.2:
        display_ratio = 1.5 # simplify to 1.5x mostly
        portion = f"1.5 Servings"
    else:
        display_ratio = 0.75
        portion = "Small Portion (0.75)"

    # Final Scaled Values
    final_kcal = int(choice["calories"] * display_ratio)
    final_p = int(choice.get("p", 0) * display_ratio)
    final_c = int(choice.get("c", 0) * display_ratio)
    final_f = int(choice.get("f", 0) * display_ratio)

    return {
        "name": choice["name"], 
        "calories": final_kcal,
        "protein": final_p,
        "carbs": final_c,
        "fats": final_f,
        "portion": portion
    }

def pick_foods_for_calories(df, target_kcal, diet_pref, meal_type):
    # 60% chance to use Curated (Higher quality data)
    if random.random() > 0.4:
        return [pick_from_curated(diet_pref, meal_type, target_kcal)]

    if df is None or df.empty or "calories" not in df.columns:
        return [pick_from_curated(diet_pref, meal_type, target_kcal)]

    candidates = df[df["calories"] <= target_kcal * 1.1]
    if candidates.empty: candidates = df

    try:
        candidates = candidates.copy() # Avoid settingoncopy warning
        candidates["diff"] = abs(candidates["calories"] - target_kcal)
        best = candidates.nsmallest(20, "diff")
        if best.empty: raise Exception("No match")
        
        choice = best.sample(1).iloc[0]
        
        # Grab macros from DF if they exist, else 0
        p = int(choice["p"]) if "p" in choice else 0
        c = int(choice["c"]) if "c" in choice else 0
        f = int(choice["f"]) if "f" in choice else 0
        
        return [{
            "name": str(choice["food"]).title(),
            "calories": int(choice["calories"]),
            "protein": p,
            "carbs": c,
            "fats": f,
            "portion": "1 Serving"
        }]
    except:
        return [pick_from_curated(diet_pref, meal_type, target_kcal)]


def get_meal_plan(target_calories, diet_pref="Veg", goal="maintenance"):
    df = load_food_dataframe()
    diet_pref = diet_pref.lower()
    
    df_filtered = None
    if df is not None:
        df_filtered = df.copy()
        if diet_pref == "veg" and "is_veg" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["is_veg"] == 1]
        elif diet_pref == "vegan":
            df_filtered = df_filtered[~df_filtered["food"].str.contains("milk|cheese|egg|butter|yogurt|cream", case=False, na=False)]

    weights = {"Breakfast": 0.25, "Lunch": 0.35, "Dinner": 0.30, "Snacks": 0.10}
    plan = {}
    
    total_plan_p = 0
    total_plan_c = 0
    total_plan_f = 0

    for meal_name, weight in weights.items():
        meal_kcal = int(target_calories * weight)
        items = pick_foods_for_calories(df_filtered, meal_kcal, diet_pref, meal_name)
        
        # Accumulate totals to check later if you want
        for item in items:
            total_plan_p += item.get("protein", 0)
            total_plan_c += item.get("carbs", 0)
            total_plan_f += item.get("fats", 0)
            
        plan[meal_name] = items

    # Optional: You could return these totals to the frontend to show "Actual vs Target"
    return plan

# ----------------------------------------------------------------------
# 6. INPUT VALIDATION
# ----------------------------------------------------------------------
def validate_inputs(form):
    data, errors = {}, {}
    def get(k): return form.get(k)

    try:
        data["age"] = int(get("age"))
        if not (10 <= data["age"] <= 100): errors["age"] = "Age 10-100"
    except: errors["age"] = "Invalid age"

    try:
        data["height"] = float(get("height"))
        if not (50 <= data["height"] <= 300): errors["height"] = "Height realistic"
    except: errors["height"] = "Invalid height"

    try:
        data["weight"] = float(get("weight"))
        if not (20 <= data["weight"] <= 500): errors["weight"] = "Weight realistic"
    except: errors["weight"] = "Invalid weight"

    data["gender"] = get("gender") or "Male"
    data["activity"] = get("activity") or "Sedentary"
    data["goal"] = get("goal") or "Maintenance"
    data["diet"] = get("diet") or "Veg"

    return data, errors