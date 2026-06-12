import pandas as pd
from tkinter import Tk, filedialog

# Create a Tkinter window
root = Tk()
root.withdraw()  # Hide the root window

# Ask the user to select a file
file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))

# Load the CSV file
df = pd.read_csv(file_path, skiprows=1, parse_dates=['Gerätezeitstempel'], dayfirst=True)

# Combine "Glukosewert-Verlauf mg/dL" and "Glukose-Scan mg/dL" into a single column
df['BG'] = df['Glukosewert-Verlauf mg/dL'].combine_first(df['Glukose-Scan mg/dL'])

# Attempt to convert "BG" to floats, safely handling non-numeric values
df['BG'] = pd.to_numeric(df['BG'], errors='coerce')

# Now drop any rows where 'BG' could not be converted to a number (and thus is NaN)
df = df.dropna(subset=['BG'])

# Round and convert to int
df['BG'] = df['BG'].astype(float).round(0).astype(int)

# Keep only the necessary columns and rename them
df = df[['Gerätezeitstempel', 'BG']]
df.rename(columns={'Gerätezeitstempel': 'Date'}, inplace=True)

# Format the "Date" to the desired string format "DD-MM-YYYY HH:MM"
df['Date'] = df['Date'].dt.strftime('%d-%m-%Y %H:%M')

# Define the specific date and time ranges to keep
time_ranges = [
    ("21-09-2025 02:25", "21-09-2025 08:24"),
    ("17-09-2025 00:19", "17-09-2025 07:19"),
]

# Re-parse the "Date" to ensure proper filtering since we've changed its format
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y %H:%M')

# Filter the data based on the specified date and time ranges
filtered_df = pd.DataFrame()
for start, end in time_ranges:
    start_dt = pd.to_datetime(start, dayfirst=True)
    end_dt = pd.to_datetime(end, dayfirst=True)
    mask = (df['Date'] >= start_dt) & (df['Date'] <= end_dt)
    filtered_df = pd.concat([filtered_df, df.loc[mask]])

# Convert "Date" back to the desired string format "DD-MM-YYYY HH:MM" for final output
filtered_df['Date'] = filtered_df['Date'].dt.strftime('%d-%m-%Y %H:%M')

# Sort the dataframe by "Date" in descending order
filtered_df.sort_values(by='Date', ascending=True, inplace=True)

# Save the cleaned and filtered data to a new CSV file
filtered_df.to_csv('filtered_glucose.csv', index=False)

print("Data processing complete. The filtered data is saved in 'filtered_glucose.csv'.")

