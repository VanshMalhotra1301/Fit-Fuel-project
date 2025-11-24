import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def train_and_save_model():
    print("🚀 Starting Model Training Process...")

    # 1. Load Data
    # Ensure calories.csv is in the same folder as this script
    csv_path = 'calories.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: '{csv_path}' not found.")
        print("Please download 'calories.csv' and place it in this folder.")
        return

    print(f"📂 Loading dataset from {csv_path}...")
    data = pd.read_csv(csv_path)

    # 2. Preprocessing
    # Your dataset columns: User_ID, Gender, Age, Height, Weight, Duration, Heart_Rate, Body_Temp, Calories
    
    # Check for null values
    if data.isnull().sum().sum() > 0:
        print("⚠️  Warning: Missing values found. Dropping missing rows...")
        data = data.dropna()

    # Encode Gender (Male: 1, Female: 0)
    # The LabelEncoder will automatically assign 0/1 based on alphabetical order usually (female=0, male=1)
    print("⚙️  Encoding categorical data...")
    le = LabelEncoder()
    data['Gender'] = le.fit_transform(data['Gender'])
    
    # Print mapping to be sure (Optional debug info)
    # 0 = Female, 1 = Male (usually)
    print(f"   Gender Mapping: {dict(zip(le.classes_, le.transform(le.classes_)))}")

    # Features (X) - We exclude User_ID and Body_Temp (Temp is result of exercise, not input predictor usually)
    # We include Duration & Heart_Rate because the app will simulate these based on "Activity Level"
    X = data[['Gender', 'Age', 'Height', 'Weight', 'Duration', 'Heart_Rate']]
    
    # Target (y) - Calories burned
    y = data['Calories']

    # 3. Train Test Split
    print("✂️  Splitting data into training and testing sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Train Model
    print("🧠 Training Random Forest Regressor (this may take a moment)...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate (Optional)
    score = model.score(X_test, y_test)
    print(f"✅ Model Training Complete! R^2 Score: {score:.4f}")

    # 5. Save Model
    # Create 'models' directory if it doesn't exist
    if not os.path.exists('models'):
        os.makedirs('models')
    
    save_path = 'models/calorie_model.pkl'
    joblib.dump(model, save_path)
    print(f"💾 Model saved successfully to: {save_path}")

if __name__ == "__main__":
    train_and_save_model()