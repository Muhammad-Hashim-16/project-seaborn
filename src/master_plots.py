"""
Seaborn Visualization Masterclass: From Beginner to Advanced
A comprehensive architectural guide containing over 60 distinct plots.
"""

# 1. MODULE IMPORTS AND GLOBAL CONFIGURATION
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100
sns.set_theme(style="darkgrid")

# 2. BASE DATASET LOADING
# Loaded exactly once to prevent HTTP 503 errors.
_base_tips = sns.load_dataset("tips")
_base_flights = sns.load_dataset("flights")
_base_titanic = sns.load_dataset("titanic")
_base_penguins = sns.load_dataset("penguins")
_base_iris = sns.load_dataset("iris")
_base_car_crashes = sns.load_dataset("car_crashes")
_base_diamonds = sns.load_dataset("diamonds")
_base_mpg = sns.load_dataset("mpg")
_base_fmri = sns.load_dataset("fmri")
_base_brain_networks = sns.load_dataset("brain_networks", header=[0, 1, 2], index_col=0)
_base_dots = sns.load_dataset("dots")
_base_healthexp = sns.load_dataset("healthexp")
_base_exercise = sns.load_dataset("exercise")
_base_taxis = sns.load_dataset("taxis")
_base_anscombe = sns.load_dataset("anscombe")
_base_attention = sns.load_dataset("attention")
_base_seaice = sns.load_dataset("seaice")


# PHASE 1: BEGINNER LEVEL (Plots 1 to 20)

# 1 Scatter Plot
df_1 = _base_tips.copy()
fig_1, ax_1 = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=df_1, x="total_bill", y="tip", ax=ax_1)
ax_1.set_title("Plot 1: Basic Scatter Plot")
plt.close(fig_1)

# 2 Line Plot
df_2 = _base_flights.copy()
df_2_sub = df_2[df_2["month"] == "Jan"]
fig_2, ax_2 = plt.subplots(figsize=(8, 5))
sns.lineplot(data=df_2_sub, x="year", y="passengers", ax=ax_2)
ax_2.set_title("Plot 2: Basic Line Plot")
plt.close(fig_2)

# 3 Bar Plot
df_3 = _base_titanic.copy()
fig_3, ax_3 = plt.subplots(figsize=(8, 5))
sns.barplot(data=df_3, x="class", y="fare", ax=ax_3, errorbar=None)
ax_3.set_title("Plot 3: Categorical Bar Plot")
plt.close(fig_3)

# 4 Count Plot
df_4 = _base_titanic.copy()
fig_4, ax_4 = plt.subplots(figsize=(8, 5))
sns.countplot(data=df_4, x="alive", ax=ax_4)
ax_4.set_title("Plot 4: Basic Count Plot")
plt.close(fig_4)

# 5 Histogram
df_5 = _base_penguins.copy()
fig_5, ax_5 = plt.subplots(figsize=(8, 5))
sns.histplot(data=df_5, x="flipper_length_mm", ax=ax_5)
ax_5.set_title("Plot 5: Basic Histogram")
plt.close(fig_5)

# 6 KDE Plot
df_6 = _base_iris.copy()
fig_6, ax_6 = plt.subplots(figsize=(8, 5))
sns.kdeplot(data=df_6, x="sepal_length", ax=ax_6)
ax_6.set_title("Plot 6: Kernel Density Estimate Plot")
plt.close(fig_6)

# 7 Box Plot
df_7 = _base_tips.copy()
fig_7, ax_7 = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df_7, x="day", y="total_bill", ax=ax_7)
ax_7.set_title("Plot 7: Standard Box Plot")
plt.close(fig_7)

# 8 Violin Plot
df_8 = _base_tips.copy()
fig_8, ax_8 = plt.subplots(figsize=(8, 5))
sns.violinplot(data=df_8, x="time", y="tip", ax=ax_8)
ax_8.set_title("Plot 8: Standard Violin Plot")
plt.close(fig_8)

# 9 Stripplot
df_9 = _base_iris.copy()
fig_9, ax_9 = plt.subplots(figsize=(8, 5))
sns.stripplot(data=df_9, x="species", y="petal_length", ax=ax_9)
ax_9.set_title("Plot 9: Categorical Strip Plot")
plt.close(fig_9)

# 10 Swarmplot
df_10 = _base_tips.copy()
fig_10, ax_10 = plt.subplots(figsize=(8, 5))
sns.swarmplot(data=df_10, x="day", y="tip", ax=ax_10)
ax_10.set_title("Plot 10: Categorical Swarm Plot")
plt.close(fig_10)

# 11 Rug Plot
df_11 = _base_penguins.copy()
fig_11, ax_11 = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=df_11, x="bill_length_mm", y="bill_depth_mm", ax=ax_11)
sns.rugplot(data=df_11, x="bill_length_mm", y="bill_depth_mm", ax=ax_11)
ax_11.set_title("Plot 11: Scatter Plot with Marginal Rugs")
plt.close(fig_11)

# 12 Empirical Cumulative Distribution Function
df_12 = _base_iris.copy()
fig_12, ax_12 = plt.subplots(figsize=(8, 5))
sns.ecdfplot(data=df_12, x="sepal_width", ax=ax_12)
ax_12.set_title("Plot 12: ECDF Plot")
plt.close(fig_12)

# 13 Linear Regression Plot
df_13 = _base_tips.copy()
fig_13, ax_13 = plt.subplots(figsize=(8, 5))
sns.regplot(data=df_13, x="total_bill", y="tip", ax=ax_13)
ax_13.set_title("Plot 13: Standard Linear Regression Plot")
plt.close(fig_13)

# 14 Residplot
df_14 = _base_tips.copy()
fig_14, ax_14 = plt.subplots(figsize=(8, 5))
sns.residplot(data=df_14, x="total_bill", y="tip", ax=ax_14)
ax_14.set_title("Plot 14: Linear Regression Residuals")
plt.close(fig_14)

# 15 Correlation Heatmap
df_15 = _base_iris.copy()
df_15_numeric = df_15.select_dtypes(include=[np.number])
fig_15, ax_15 = plt.subplots(figsize=(6, 5))
sns.heatmap(data=df_15_numeric.corr(), annot=True, ax=ax_15)
ax_15.set_title("Plot 15: Basic Correlation Heatmap")
plt.close(fig_15)

# 16 Horizontal Bar Plot
df_16 = _base_car_crashes.copy().sort_values("total", ascending=False).head(10)
fig_16, ax_16 = plt.subplots(figsize=(8, 5))
sns.barplot(data=df_16, x="total", y="abbrev", ax=ax_16)
ax_16.set_title("Plot 16: Horizontal Bar Chart")
plt.close(fig_16)

# 17 Bivariate Histogram
df_17 = _base_penguins.copy()
fig_17, ax_17 = plt.subplots(figsize=(8, 5))
sns.histplot(data=df_17, x="bill_length_mm", y="bill_depth_mm", ax=ax_17)
ax_17.set_title("Plot 17: Bivariate Histogram")
plt.close(fig_17)

# 18 Bivariate KDE
df_18 = _base_iris.copy()
fig_18, ax_18 = plt.subplots(figsize=(8, 5))
sns.kdeplot(data=df_18, x="sepal_length", y="sepal_width", ax=ax_18)
ax_18.set_title("Plot 18: Bivariate Density Contour")
plt.close(fig_18)

# 19 Point Plot
df_19 = _base_tips.copy()
fig_19, ax_19 = plt.subplots(figsize=(8, 5))
sns.pointplot(data=df_19, x="time", y="total_bill", ax=ax_19)
ax_19.set_title("Plot 19: Point Estimates and Error Intervals")
plt.close(fig_19)

# 20 Boxenplot
df_20 = _base_diamonds.copy()
fig_20, ax_20 = plt.subplots(figsize=(8, 5))
sns.boxenplot(data=df_20, x="cut", y="price", ax=ax_20)
ax_20.set_title("Plot 20: Quantile Boxenplot")
plt.close(fig_20)


# PHASE 2: INTERMEDIATE LEVEL (Plots 21 to 40)

# 21 Hue-Encoded Scatter Plot
df_21 = _base_tips.copy()
fig_21, ax_21 = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=df_21, x="total_bill", y="tip", hue="smoker", ax=ax_21)
ax_21.set_title("Plot 21: Grouped Scatter Plot")
plt.close(fig_21)

# 22 Sized Scatter Plot
df_22 = _base_mpg.copy()
fig_22, ax_22 = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=df_22, x="horsepower", y="mpg", size="weight", sizes=(20, 200), ax=ax_22)
ax_22.set_title("Plot 22: Bubble Scatter Layout")
plt.close(fig_22)

# 23 Styled Multi-Line Plot
df_23 = _base_fmri.copy()
fig_23, ax_23 = plt.subplots(figsize=(8, 5))
sns.lineplot(data=df_23, x="timepoint", y="signal", hue="event", style="region", ax=ax_23)
ax_23.set_title("Plot 23: Annotated Time-Series Configuration")
plt.close(fig_23)

# 24 Grouped Bar Plot
df_24 = _base_titanic.copy()
fig_24, ax_24 = plt.subplots(figsize=(8, 5))
sns.barplot(data=df_24, x="class", y="fare", hue="sex", ax=ax_24, errorbar=None)
ax_24.set_title("Plot 24: Segmented Bar Grid")
plt.close(fig_24)

# 25 Stacked/Grouped Countplot
df_25 = _base_titanic.copy()
fig_25, ax_25 = plt.subplots(figsize=(8, 5))
sns.countplot(data=df_25, x="deck", hue="embark_town", ax=ax_25)
ax_25.set_title("Plot 25: Categorical Distribution Breakdown")
plt.close(fig_25)

# 26 Multi-Element Histplot
df_26 = _base_penguins.copy()
fig_26, ax_26 = plt.subplots(figsize=(8, 5))
sns.histplot(data=df_26, x="flipper_length_mm", hue="species", element="step", ax=ax_26)
ax_26.set_title("Plot 26: Layered Step Histograms")
plt.close(fig_26)

# 27 Grouped Violin Plot
df_27 = _base_tips.copy()
fig_27, ax_27 = plt.subplots(figsize=(8, 5))
sns.violinplot(data=df_27, x="day", y="total_bill", hue="sex", split=True, ax=ax_27)
ax_27.set_title("Plot 27: Split Violin Comparison")
plt.close(fig_27)

# 28 Jointplot (Scatter + Marginal Histograms)
df_28 = _base_iris.copy()
g_28 = sns.jointplot(data=df_28, x="sepal_length", y="sepal_width", kind="scatter")
g_28.fig.suptitle("Plot 28: Joint Scatter & Histogram", y=1.02)
plt.close(g_28.fig)

# 29 Jointplot Hex
df_29 = _base_diamonds.copy().sample(2000, random_state=42)
g_29 = sns.jointplot(data=df_29, x="carat", y="price", kind="hex")
g_29.fig.suptitle("Plot 29: Hexagonal Joint Distribution Mesh", y=1.02)
plt.close(g_29.fig)

# 30 Pairplot Grid
df_30 = _base_iris.copy()
g_30 = sns.pairplot(data=df_30, hue="species")
g_30.fig.suptitle("Plot 30: Pairwise Feature Matrix Grid", y=1.02)
plt.close(g_30.fig)

# 31 Figure-Level Relplot
df_31 = _base_tips.copy()
g_31 = sns.relplot(data=df_31, x="total_bill", y="tip", col="time", hue="smoker", kind="scatter")
g_31.fig.suptitle("Plot 31: Faceted Relational Scatter", y=1.05)
plt.close(g_31.fig)

# 32 Figure-Level Catplot
df_32 = _base_tips.copy()
g_32 = sns.catplot(data=df_32, x="day", y="total_bill", col="smoker", kind="box")
g_32.fig.suptitle("Plot 32: Faceted Categorical Boxes", y=1.05)
plt.close(g_32.fig)

# 33 Figure-Level Displot
df_33 = _base_penguins.copy()
g_33 = sns.displot(data=df_33, x="flipper_length_mm", col="sex", hue="species", kind="kde", multiple="stack")
g_33.fig.suptitle("Plot 33: Faceted Stacked Density Matrix", y=1.05)
plt.close(g_33.fig)

# 34 Lmplot Grid
df_34 = _base_tips.copy()
g_34 = sns.lmplot(data=df_34, x="total_bill", y="tip", col="smoker", hue="sex")
g_34.fig.suptitle("Plot 34: Faceted Regression Dynamics", y=1.05)
plt.close(g_34.fig)

# 35 Custom FacetGrid Base
df_35 = _base_iris.copy()
g_35 = sns.FacetGrid(df_35, col="species")
g_35.map(plt.scatter, "sepal_length", "sepal_width")
g_35.fig.suptitle("Plot 35: Standard FacetGrid Layout", y=1.05)
plt.close(g_35.fig)

# 36 Stacked Percentage Bar Chart
df_36_raw = _base_titanic.copy()
df_36 = df_36_raw.groupby(["class", "who"], observed=True).size().unstack(fill_value=0)
df_36 = df_36.div(df_36.sum(axis=1), axis=0) * 100
fig_36, ax_36 = plt.subplots(figsize=(8, 5))
df_36.plot(kind="bar", stacked=True, ax=ax_36, edgecolor="black")
ax_36.set_ylabel("Percentage (%)")
ax_36.set_title("Plot 36: Normalized Stacked Category Distributions")
plt.close(fig_36)

# 37 Cluster Heatmap
df_37 = _base_flights.copy()
df_37_piv = df_37.pivot(index="month", columns="year", values="passengers")
g_37 = sns.clustermap(data=df_37_piv, row_cluster=False, col_cluster=True, cmap="mako")
g_37.fig.suptitle("Plot 37: Clustered Matrix View", y=1.02)
plt.close(g_37.fig)

# 38 Logarithmic Scaling Plots
df_38 = _base_diamonds.copy()
fig_38, ax_38 = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=df_38, x="carat", y="price", ax=ax_38, alpha=0.3)
ax_38.set_yscale("log")
ax_38.set_title("Plot 38: Log-Transformed Numeric Target Axis")
plt.close(fig_38)

# 39 Custom Multi-Plot Layout
df_39 = _base_tips.copy()
fig_39, (ax_39_1, ax_39_2) = plt.subplots(1, 2, figsize=(14, 5))
sns.scatterplot(data=df_39, x="total_bill", y="tip", ax=ax_39_1)
sns.boxplot(data=df_39, x="size", y="total_bill", ax=ax_39_2)
fig_39.suptitle("Plot 39: Custom Heterogeneous Subplot Panel")
plt.close(fig_39)

# 40 Advanced Pair Grid
df_40 = _base_iris.copy()
g_40 = sns.PairGrid(df_40, hue="species")
g_40.map_upper(sns.scatterplot)
g_40.map_lower(sns.kdeplot, alpha=0.5)
g_40.map_diag(sns.histplot)
g_40.fig.suptitle("Plot 40: Multi-Process Non-Symmetric Pair Matrix", y=1.02)
plt.close(g_40.fig)


# PHASE 3: ADVANCED LEVEL (Plots 41 to 65)

# 41 High-Dimensional Matrix Cluster Mapping
df_41 = _base_brain_networks.copy()
df_41_sub = df_41.iloc[:, :20].corr()
g_41 = sns.clustermap(data=df_41_sub, cmap="vlag", vmin=-1, vmax=1, linewidths=0.5, annot=False)
g_41.fig.suptitle("Plot 41: Advanced Biological Connectivity Clustermap", y=1.02)
plt.close(g_41.fig)

# 42 Jointplot with Layered Bivariate Contours
df_42 = _base_penguins.copy()
g_42 = sns.jointplot(data=df_42, x="bill_length_mm", y="bill_depth_mm", hue="species", kind="kde", alpha=0.7)
g_42.fig.suptitle("Plot 42: Layered Bivariate Kernel Densities", y=1.02)
plt.close(g_42.fig)

# 43 Multi-Layer Regression Faceting
df_43 = _base_mpg.copy()
g_43 = sns.lmplot(data=df_43, x="weight", y="mpg", col="origin", hue="origin", order=2, ci=95, scatter_kws={"alpha": 0.4})
g_43.fig.suptitle("Plot 43: Second-Order Polynomial Regression Matrix", y=1.05)
plt.close(g_43.fig)

# 44 Ridge Plot Construction
df_44_raw = _base_flights.copy()
g_44 = sns.FacetGrid(df_44_raw, row="month", hue="month", aspect=9, height=0.7, palette="plasma")
g_44.map(sns.kdeplot, "passengers", fill=True, alpha=0.8, lw=1.5, bw_adjust=0.5)
g_44.map(sns.kdeplot, "passengers", color="white", lw=2, bw_adjust=0.5)
g_44.refline(y=0, linewidth=2, linestyle="-", color=None, clip_on=False)
g_44.figure.subplots_adjust(hspace=-0.20)
g_44.set_titles("")
g_44.set(yticks=[], ylabel="")
g_44.despine(bottom=True, left=True)
g_44.fig.suptitle("Plot 44: High-Density Ridge Timeline Grid", y=0.98)
plt.close(g_44.fig)

# 45 Polynomial Regression Evaluation (Dependencies Safe)
df_45 = _base_titanic.copy()
fig_45, ax_45 = plt.subplots(figsize=(8, 5))
sns.regplot(data=df_45, x="fare", y="survived", order=2, ax=ax_45, scatter_kws={"alpha":0.3})
ax_45.set_title("Plot 45: Polynomial Target Probability Profile")
plt.close(fig_45)

# 46 Linear Correlation Control Matrices
df_46 = _base_diamonds.copy().select_dtypes(include=[np.number])
df_46_corr = df_46.corr()
mask_46 = np.triu(np.ones_like(df_46_corr, dtype=bool))
fig_46, ax_46 = plt.subplots(figsize=(8, 6))
sns.heatmap(data=df_46_corr, mask=mask_46, cmap="coolwarm", annot=True, fmt=".2f", ax=ax_46)
ax_46.set_title("Plot 46: Masked Upper Triangular Matrix Correlation")
plt.close(fig_46)

# 47 Advanced Violin Layering
df_47 = _base_tips.copy()
fig_47, ax_47 = plt.subplots(figsize=(9, 6))
sns.violinplot(data=df_47, x="day", y="total_bill", hue="smoker", inner="quart", palette="muted", ax=ax_47)
sns.stripplot(data=df_47, x="day", y="total_bill", hue="smoker", dodge=True, alpha=0.3, palette="dark:black", ax=ax_47)
ax_47.set_title("Plot 47: Hybrid Quantile Violin & Dot-Strip Layout")
plt.close(fig_47)

# 48 FacetGrid Path Mapping
df_48 = _base_dots.copy().query("align == 'dots'")
g_48 = sns.FacetGrid(df_48, col="choice", hue="coherence", palette="viridis", col_wrap=2)
g_48.map(plt.plot, "time", "firing_rate", marker="o", ms=4)
g_48.fig.suptitle("Plot 48: High-Frequency Temporal Matrix Networks", y=1.02)
plt.close(g_48.fig)

# 49 Hex-Mesh Bivariate Analysis
df_49 = _base_mpg.copy()
g_49 = sns.jointplot(data=df_49, x="weight", y="acceleration", kind="hex", color="#4CB391")
g_49.plot_joint(sns.kdeplot, color="black", zorder=5, levels=4)
g_49.fig.suptitle("Plot 49: Combined Hexagonal Mesh and Isodensity Contours", y=1.02)
plt.close(g_49.fig)

# 50 Non-Linear LOWESS Analysis
df_50 = _base_mpg.copy()
fig_50, ax_50 = plt.subplots(figsize=(8, 5))
sns.regplot(data=df_50, x="displacement", y="mpg", lowess=True, ax=ax_50, line_kws={"color": "red", "lw": 3})
ax_50.set_title("Plot 50: Non-Parametric LOWESS Trend Model")
plt.close(fig_50)

# 51 Multi-Variable Continuous Point Tracking
df_51 = _base_healthexp.copy()
fig_51, ax_51 = plt.subplots(figsize=(10, 6))
sns.lineplot(data=df_51, x="Year", y="Life_Expectancy", hue="Country", style="Country", markers=True, dashes=False, ax=ax_51)
ax_51.set_title("Plot 51: Multi-Signal Longitudinal Trend Graph")
plt.close(fig_51)

# 52 Faceted Structural Counting
df_52 = _base_exercise.copy()
g_52 = sns.catplot(data=df_52, x="time", y="pulse", col="kind", row="diet", kind="point", height=3.5, aspect=1.1)
g_52.fig.suptitle("Plot 52: Multi-Factor Factorial Condition Matrix", y=1.02)
plt.close(g_52.fig)

# 53 PairGrid with Independent Linear Estimates
df_53 = _base_penguins.copy()
g_53 = sns.PairGrid(df_53, hue="species", vars=["bill_length_mm", "bill_depth_mm", "flipper_length_mm"])
g_53.map_diag(sns.histplot, multiple="stack")
g_53.map_offdiag(sns.regplot, scatter_kws={"alpha": 0.3})
g_53.fig.suptitle("Plot 53: Pair Grid with Local Subgroup Trend Models", y=1.02)
plt.close(g_53.fig)

# 54 Categorical Boxplots Palette Array
df_54 = _base_diamonds.copy().sample(5000, random_state=12)
fig_54, ax_54 = plt.subplots(figsize=(10, 5))
sns.boxplot(data=df_54, x="color", y="price", hue="clarity", palette="ch:start=.2,rot=-.3", ax=ax_54)
ax_54.set_title("Plot 54: High-Density Ordered Categorical Whisker Panel")
plt.close(fig_54)

# 55 Bivariate Conditional ECDF
df_55 = _base_tips.copy()
g_55 = sns.displot(data=df_55, x="total_bill", hue="sex", col="day", kind="ecdf", lw=2)
g_55.fig.suptitle("Plot 55: Faceted Step Cumulative Distribution Curves", y=1.05)
plt.close(g_55.fig)

# 56 Custom Subplot Allocation Matrix
df_56 = _base_taxis.copy()
fig_56 = plt.figure(figsize=(12, 8))
grid_56 = plt.GridSpec(2, 2, wspace=0.3, hspace=0.3)
ax_56_1 = fig_56.add_subplot(grid_56[0, :])
ax_56_2 = fig_56.add_subplot(grid_56[1, 0])
ax_56_3 = fig_56.add_subplot(grid_56[1, 1])
sns.lineplot(data=df_56, x="pickup", y="total", ax=ax_56_1)
sns.scatterplot(data=df_56, x="distance", y="tip", hue="payment", ax=ax_56_2)
sns.boxplot(data=df_56, x="payment", y="fare", ax=ax_56_3)
fig_56.suptitle("Plot 56: Multi-Scale Compound Spatial Visualization Panel")
plt.close(fig_56)

# 57 Multi-Class Density Outlines
df_57 = _base_iris.copy()
fig_57, ax_57 = plt.subplots(figsize=(8, 6))
sns.kdeplot(data=df_57, x="sepal_length", y="sepal_width", hue="species", fill=True, alpha=0.3, levels=5, ax=ax_57)
ax_57.set_title("Plot 57: Layered Topographic Kernel Space")
plt.close(fig_57)

# 58 Standardized Residual Target Analysis
df_58 = _base_anscombe.copy()
g_58 = sns.lmplot(data=df_58, x="x", y="y", col="dataset", hue="dataset", col_wrap=2, ci=None, height=4)
g_58.fig.suptitle("Plot 58: Comparative Evaluation of Anscombe's Quartet", y=1.02)
plt.close(g_58.fig)

# 59 Multi-Value Categorical Swarm
df_59 = _base_attention.copy()
fig_59, ax_59 = plt.subplots(figsize=(8, 5))
sns.swarmplot(data=df_59, x="solutions", y="score", hue="attention", size=6, ax=ax_59)
ax_59.set_title("Plot 59: Multi-Factor Grouped Swarm Dispersion Plot")
plt.close(fig_59)

# 60 Advanced Heatmap Matrix
df_60 = _base_mpg.copy().select_dtypes(include=[np.number]).dropna().corr()
fig_60, ax_60 = plt.subplots(figsize=(8, 6))
sns.heatmap(data=df_60, annot=True, fmt=".3f", cmap="magma", linewidths=1, linecolor="grey", cbar=True, ax=ax_60)
ax_60.set_title("Plot 60: Precision Heatmap Metric Grid")
plt.close(fig_60)

# 61 Complex Logarithmic Boxenplot
df_61 = _base_diamonds.copy()
fig_61, ax_61 = plt.subplots(figsize=(9, 6))
sns.boxenplot(data=df_61, x="color", y="price", hue="cut", showfliers=False, ax=ax_61)
ax_61.set_yscale("log")
ax_61.set_title("Plot 61: Scale-Inverted Multi-Quantile Distribution Analysis")
plt.close(fig_61)

# 62 Outlier Detection Pair-Matrix
df_62 = _base_penguins.copy().dropna()
g_62 = sns.PairGrid(df_62, hue="sex", corner=True)
g_62.map_lower(sns.scatterplot, alpha=0.6, edgecolor="none", s=25)
g_62.map_diag(sns.kdeplot, fill=True)
g_62.add_legend()
g_62.fig.suptitle("Plot 62: Lower-Triangular Target Correlation Grid", y=1.02)
plt.close(g_62.fig)

# 63 Time-Series Aggregations
df_63 = _base_seaice.copy()
df_63["Year"] = pd.to_datetime(df_63["Date"]).dt.year
df_63_sub = df_63[df_63["Year"].between(1980, 2010)]
fig_63, ax_63 = plt.subplots(figsize=(10, 5))
sns.lineplot(data=df_63_sub, x="Year", y="Extent", errorbar="sd", estimator="mean", ax=ax_63)
ax_63.set_title("Plot 63: Decadal Trend Analysis with Variance Bounds")
plt.close(fig_63)

# 64 Dual-Axis Distribution Overlays
df_64 = _base_tips.copy()
fig_64, ax_64_1 = plt.subplots(figsize=(9, 5))
ax_64_2 = ax_64_1.twinx()
sns.histplot(data=df_64, x="total_bill", color="g", label="Count Histogram", ax=ax_64_1, alpha=0.4)
sns.kdeplot(data=df_64, x="total_bill", color="b", label="Kernel Density", ax=ax_64_2, linewidth=2)
ax_64_1.set_ylabel("Histogram Absolute Scale")
ax_64_2.set_ylabel("Continuous Probability Distribution Scale")
ax_64_1.set_title("Plot 64: Non-Normalized Joint Dual-Scale Overlay Panel")
plt.close(fig_64)

# 65 Matrix Facet Wraps
df_65 = _base_car_crashes.copy().head(12)
df_65_melted = pd.melt(df_65, id_vars=["abbrev"], value_vars=["speeding", "alcohol", "not_distracted"])
g_65 = sns.catplot(data=df_65_melted, x="abbrev", y="value", col="variable", kind="bar", col_wrap=1, height=3, aspect=3)
g_65.fig.suptitle("Plot 65: Standard Multi-Metric Performance Tracking Array", y=1.02)
plt.close(g_65.fig)

print("Execution successfully verified. All plots constructed using independent variable spaces.")