from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

master = pd.read_csv("master_dataset.csv")

x = master['poverty_rate']
y = master['avg_allowance_rate']

# 1. Correlation + p-value
corr, p_value = stats.pearsonr(x, y)

# 2. Effect size (r-squared)
r_squared = corr ** 2

# 3. Interpretation
if abs(corr) >= 0.5:
    strength = "strong"
elif abs(corr) >= 0.3:
    strength = "moderate"
else:
    strength = "weak"

print(f"Correlation: {round(corr, 3)}")
print(f"P-value: {round(p_value, 4)} → {'Significant' if p_value < 0.05 else 'Not significant'}")
print(f"R-squared: {round(r_squared, 3)} → poverty rate explains {round(r_squared*100, 1)}% of approval rate variance")
print(f"Strength: {strength}")

# 4. Visualization
plt.figure(figsize=(8, 5))
plt.scatter(x, y, alpha=0.6, color='steelblue')

# Add regression line
m, b = np.polyfit(x, y, 1)
plt.plot(x, m*x + b, color='red', linewidth=2)

# Add state labels
for i, row in master.iterrows():
    plt.annotate(row['State Code'], 
                (row['poverty_rate'], row['avg_allowance_rate']),
                fontsize=7, alpha=0.7)

plt.xlabel('Poverty Rate (%)')
plt.ylabel('Avg Allowance Rate (%)')
plt.title(f'H1: Poverty Rate vs Approval Rate (r={round(corr,3)}, p={round(p_value,4)})')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()