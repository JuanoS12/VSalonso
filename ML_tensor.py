import numpy as np
import pickle
from sklearn.linear_model import LinearRegression
import time

# ================================
# Part 1: Train the Regression Model
# ================================
def train_model():
    """
    Trains a regression model to predict the time to reach a critical fill level.
    """
    # Simulated training data: [Fill Level, Rate of Fill] -> Time to Critical Level
    # Fill Level (0-1), Rate of Fill (0-1 per hour)
    X_train = np.array([
        [0.2, 0.01],  # 20% full, filling at 1% per hour
        [0.3, 0.015],  # 30% full, filling at 1.5% per hour
        [0.5, 0.02],  # 50% full, filling at 2% per hour
        [0.6, 0.025],  # 60% full, filling at 2.5% per hour
        [0.8, 0.03],  # 80% full, filling at 3% per hour
    ])
    y_train = np.array([8, 6, 4, 3, 1])  # Time to reach 90% full in hours

    # Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Save the trained model to a file
    with open("fill_level_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("Model trained and saved as 'fill_level_model.pkl'.")

# ================================
# Part 2: Use the Model for Prediction
# ================================
def load_model():
    """
    Loads the trained model from a file.
    """
    with open("fill_level_model.pkl", "rb") as f:
        model = pickle.load(f)
    return model

def predict_time_to_collect(model, fill_level, rate_of_fill):
    """
    Predicts the time to reach a critical fill level based on current conditions.
    """
    # Prepare the input data
    input_data = np.array([[fill_level, rate_of_fill]])

    # Make the prediction
    predicted_time = model.predict(input_data)

    return predicted_time[0]

# ================================
# Part 3: Simulate Sensor Readings (for real deployment)
# ================================
def simulate_sensor_readings():
    """
    Simulates sensor readings for fill level and rate of fill.
    Replace with actual sensor integration in real deployment.
    """
    # Simulated values (replace with sensor readings in deployment)
    fill_level = np.random.uniform(0.3, 0.8)  # Current fill level (30% - 80%)
    rate_of_fill = np.random.uniform(0.01, 0.03)  # Fill rate (1% - 3% per hour)
    return fill_level, rate_of_fill

# ================================
# Part 4: Main Function
# ================================
def main():
    # Train the model (only run once or as needed)
    train_model()

    # Load the trained model
    model = load_model()

    # Simulate a monitoring loop
    print("Monitoring fill levels...")
    while True:
        # Get current sensor readings
        fill_level, rate_of_fill = simulate_sensor_readings()
        print(f"Current Fill Level: {fill_level:.2f}, Rate of Fill: {rate_of_fill:.4f}")

        # Predict time to collect
        time_to_collect = predict_time_to_collect(model, fill_level, rate_of_fill)
        print(f"Predicted Time to Collect: {time_to_collect:.2f} hours")

        # Simulate periodic monitoring (e.g., every 10 seconds)
        time.sleep(10)

# ================================
# Run the Program
# ================================
if __name__ == "__main__":
    main()
