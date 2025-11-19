import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the file path
file_path = os.path.join(current_dir, 'good_practices.csv')

# Load the CSV file
df = pd.read_csv(file_path)

# Create a subfolder called "plots" if it doesn't exist
plots_dir = os.path.join(current_dir, 'plots')
if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)

# Define a function to create and save bar plots
def save_bar_plot(df, column, filename):
    plt.figure(figsize=(10, 6))
    sns.countplot(y=column, data=df, order=df[column].value_counts().index)
    plt.title(f'Distribution of {column}')
    plt.xlabel('Count')
    plt.ylabel(column)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# Define the columns to visualize
columns_to_visualize = [
    'Organisation', 'Type of Organisation', 'Country', 
    'Language', 'Key Area', 'Sector', 'Scope'
]

# Generate and save plots for each column
for column in columns_to_visualize:
    save_bar_plot(df, column, os.path.join(plots_dir, f'{column}_distribution.png'))

print("Plots have been saved in the 'plots' folder.")