%pip install pandas numpy scikit-learn matplotlib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt

# Generate sample building energy data
np.random.seed(42)
hours = np.arange(24)
temperature = 20 + 10 * np.sin(hours * np.pi / 12) + np.random.normal(0, 2, 24)
occupancy = np.where(hours < 8, 0, np.where(hours > 18, 0, 1)) + np.random.normal(0, 0.1, 24)
base_consumption = 50 + 2 * temperature + 30 * occupancy + np.random.normal(0, 5, 24)

# Create DataFrame
df = pd.DataFrame({
    'hour': hours,
    'temperature': temperature,
    'occupancy': occupancy,
    'energy_consumption': base_consumption
})

print("Sample of your building's energy data:")
print(df.head())

# Prepare features and target
X = df[['hour', 'temperature', 'occupancy']]
y = df['energy_consumption']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Calculate accuracy
mae = mean_absolute_error(y_test, predictions)
print(f"\nModel accuracy (MAE): {mae:.2f} kWh")

# Show feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nWhat drives your energy consumption:")
print(feature_importance)

# Simple visualization
plt.figure(figsize=(10, 6))
plt.scatter(y_test, predictions, alpha=0.7)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Actual Energy Consumption (kWh)')
plt.ylabel('Predicted Energy Consumption (kWh)')
plt.title('How Well Can We Predict Energy Use?')
plt.show()
