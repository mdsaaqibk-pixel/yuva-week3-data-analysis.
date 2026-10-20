"""
Week 3: Data Analysis & Python Implementation
Dataset: simulated_egovernance_data.csv
IMPORTANT: All records are illustrative synthetic data, not official government statistics.
Run: python week3_analysis.py
Dependencies: pandas, numpy, matplotlib, seaborn, scipy, scikit-learn
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "simulated_egovernance_data.csv"
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA_FILE)

# 1) Basic validation and quality checks
required = [
    "state", "applications_received", "applications_disposed",
    "pending_applications", "rejected_applications",
    "avg_processing_days", "median_processing_days",
    "citizen_satisfaction_score"
]
missing_columns = sorted(set(required) - set(df.columns))
if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")
if df[required].isna().any().any():
    print("WARNING: Missing values detected. Review before interpreting results.")
if (df[["applications_received", "applications_disposed", "pending_applications",
        "rejected_applications"]] < 0).any().any():
    raise ValueError("Application counts cannot be negative.")
if not df["citizen_satisfaction_score"].between(0, 1).all():
    raise ValueError("Satisfaction score must be between 0 and 1.")

# 2) Derived KPIs
df["disposal_rate"] = (
    df["applications_disposed"] / df["applications_received"].replace(0, np.nan)
)
df["pending_share"] = (
    df["pending_applications"] /
    (df["applications_disposed"] + df["pending_applications"]).replace(0, np.nan)
)
df["rejection_rate"] = (
    df["rejected_applications"] / df["applications_received"].replace(0, np.nan)
)
df["received_minus_disposed"] = (
    df["applications_received"] - df["applications_disposed"]
)

# 3) Summary statistics and ranked output
summary = df.select_dtypes(include="number").describe().round(3)
summary.to_csv(OUT / "summary_statistics.csv")
df.sort_values("pending_applications", ascending=False).to_csv(
    OUT / "state_kpi_table.csv", index=False
)

print("\nSummary statistics:")
print(summary)
print("\nHighest pending applications:")
print(df.nlargest(5, "pending_applications")[
    ["state", "pending_applications", "avg_processing_days", "disposal_rate"]
].to_string(index=False))

# 4) Visualizations
sns.set_theme()  # default theme; no custom color palette
plt.figure(figsize=(10, 6))
sns.barplot(data=df.sort_values("pending_applications", ascending=False),
            x="pending_applications", y="state")
plt.title("Pending Applications by State (Simulated Data)")
plt.xlabel("Pending applications")
plt.ylabel("State")
plt.tight_layout()
plt.savefig(OUT / "pending_applications_by_state.png", dpi=160)
plt.close()

plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x="avg_processing_days", y="citizen_satisfaction_score",
                size="applications_received", legend=False)
plt.title("Processing Time vs Satisfaction (Simulated Data)")
plt.xlabel("Average processing time (days)")
plt.ylabel("Citizen satisfaction score (0–1)")
plt.tight_layout()
plt.savefig(OUT / "processing_time_vs_satisfaction.png", dpi=160)
plt.close()

plt.figure(figsize=(8, 6))
sns.heatmap(df[["applications_received", "applications_disposed",
                "pending_applications", "avg_processing_days",
                "citizen_satisfaction_score", "disposal_rate"]].corr(),
            annot=True, fmt=".2f", cmap="vlag", center=0)
plt.title("Correlation Matrix (Simulated Data)")
plt.tight_layout()
plt.savefig(OUT / "correlation_matrix.png", dpi=160)
plt.close()

# 5) Correlation: association only, not causation
r, p = pearsonr(df["avg_processing_days"], df["citizen_satisfaction_score"])
(OUT / "correlation_result.txt").write_text(
    f"Pearson correlation between average processing days and satisfaction: r={r:.3f}, p={p:.4f}\n"
    "Interpret cautiously: the dataset is small and simulated. Correlation does not prove causation.\n",
    encoding="utf-8"
)

# 6) Exploratory clustering (illustrative segmentation, not a policy classification)
features = ["avg_processing_days", "pending_share", "disposal_rate",
            "citizen_satisfaction_score"]
X = df[features].replace([np.inf, -np.inf], np.nan).fillna(df[features].median())
X_scaled = StandardScaler().fit_transform(X)
model = KMeans(n_clusters=3, random_state=42, n_init=10)
df["exploratory_cluster"] = model.fit_predict(X_scaled)
df.to_csv(OUT / "analysis_results_with_clusters.csv", index=False)

print(f"\nAnalysis complete. Files saved in: {OUT}")
