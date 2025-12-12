import pandas as pd
import json

# Load the CSV data
df = pd.read_csv("static/data/fire.csv")

# Compute the variables
total_detections = len(df)
avg_frp = df["frp"].mean()
fire_data = df.to_dict("records")

# Print the results
print(df.to_dict("records"))
