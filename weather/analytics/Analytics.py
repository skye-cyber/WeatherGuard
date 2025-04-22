import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)

# Define months
months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

# Generate synthetic average temperatures (in °C) for each month
# Assuming a general temperature trend for Nairobi
average_temperatures = [
    23.5,
    24.0,
    24.5,
    23.0,
    22.0,
    21.5,
    20.5,
    21.0,
    22.5,
    23.0,
    23.5,
    24.0,
]

# Add some random noise to simulate variability
temperature_data = [temp + np.random.normal(0, 0.5) for temp in average_temperatures]

# Create a DataFrame
df = pd.DataFrame({"Month": months, "Temperature (°C)": temperature_data})

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(df["Month"], df["Temperature (°C)"], marker="o", linestyle="-")
plt.title("Synthetic Monthly Average Temperatures")
plt.xlabel("Month")
plt.ylabel("Temperature (°C)")
plt.grid(True)
plt.tight_layout()
plt.savefig("../../res/temperature_trends_graph.png")  # Save the figure
plt.show()
