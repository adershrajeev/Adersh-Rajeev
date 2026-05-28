# Technical Architecture & Context Report: Mobile Price Prediction & Deals Platform

This document provides a complete technical walkthrough of the **Mobile Phone Price Category Prediction System**. It details the directory structure, backend logic, fuzzy inference system, frontend design system, and deployment configuration.

---

## 1. Directory Structure & Key Files

The codebase is organized as follows:

```text
mobile price analysis/
└── MobilePricePrediction/
    └── MobilePricePrediction/
        ├── app.py                            # Flask application and prediction logic
        ├── requirements.txt                   # Project dependencies
        ├── run.bat                            # Setup and run script for local development
        ├── mobile_price_dataset.csv          # Base dataset (1,200 records)
        ├── Mobile_Price_Prediction_Project_Report.md   # Academic project report (Markdown)
        ├── Mobile_Price_Prediction_Project_Report.docx # Microsoft Word project report (Docx)
        │
        ├── dataset/
        │   └── data_generator.py             # Script that created/updated the dataset
        │
        ├── static/
        │   └── css/
        │       └── style.css                 # Glassmorphic UI styles, light/dark themes
        │
        ├── templates/
        │   ├── index.html                    # Homepage (Interactive mockup, range sliders)
        │   ├── predict.html                  # Prediction output (Confidence gauges, logs)
        │   ├── dashboard.html                # Analytics dashboard (Plotly, CSV analysis)
        │   └── deals.html                    # Deals & Refurbished comparison engine
        │
        └── scratch/
            ├── generate_docx.py              # Word document compilation script
            └── test_predict.py               # Unit tests for the prediction endpoint
```

---

## 2. Core Python Architecture (`app.py`)

`app.py` handles input parsing, the fuzzy engine, dataset rendering, and routing.

### 2.1 Dependencies
- **`flask`**: Serves routes, handles form parsing, and outputs templates.
- **`scikit-fuzzy` (`skfuzzy`)**: Powers the Mamdani Fuzzy Inference System (FIS).
- **`pandas` & `numpy`**: Read/write dataset parameters and manage matrix operations.
- **`plotly`**: Generates interactive HTML/JS charts dynamically on the backend dashboard.

### 2.2 Fuzzy Inference System (FIS) Configuration
The system predicts a **Price Score** (range $1.0$ to $4.0$) mapping to:
- **$[1.0 - 1.8]$**: Budget Phone
- **$[1.5 - 2.9]$**: Mid-Range Phone
- **$[2.5 - 3.7]$**: Premium Phone
- **$[3.3 - 4.0]$**: Flagship Phone

#### Antecedent Membership Functions (Six Core Inputs):
1. **RAM** ($1 - 18$ GB):
   - *Low*: Trapezoidal $[1, 1, 2, 6]$
   - *Medium*: Triangular $[4, 6, 8, 10]$
   - *High*: Trapezoidal $[8, 12, 18, 18]$
2. **Battery Power** ($2000 - 7000$ mAh):
   - *Low*: Trapezoidal $[2000, 2000, 3000, 4500]$
   - *Medium*: Triangular $[3500, 5000, 6000]$
   - *High*: Trapezoidal $[5500, 6500, 7000, 7000]$
3. **Internal Storage** ($16 - 512$ GB):
   - *Low* (16–64), *Medium* (64–256), *High* (128–512)
4. **Processor Speed** ($1.0 - 4.0$ GHz):
   - *Low* (1.0–2.0), *Medium* (1.8–2.8), *High* (2.5–4.0)
5. **Rear Camera** ($5 - 200$ MP):
   - *Low* (5–32), *Medium* (16–108), *High* (64–200)
6. **Front Camera** ($5 - 64$ MP):
   - *Low* (5–16), *Medium* (12–32), *High* (24–64)

#### Rule Evaluation Base:
A series of rules evaluates logical combinations:
- `Rule 1`: If *RAM is Low* and *Storage is Low* $\rightarrow$ *Price is Budget*
- `Rule 2`: If *RAM is High* and *Processor is High* $\rightarrow$ *Price is Flagship*
- `Rule 3`: If *RAM is Medium* and *Processor is Medium* $\rightarrow$ *Price is Mid-Range*
- `Rule 4`: If *RAM is High* or *Rear Camera is High* $\rightarrow$ *Price is Premium*
- *(Additional logical rules mapping intersections to prevent gaps)*

### 2.3 Heuristic Score Adjustment Engine
To evaluate parameters that do not map cleanly to standard continuous antecedents, a heuristic adjustment layer modifies the centroid defuzzified output $z^*$:

$$\text{Final Price Score} = \max\left(1.0, \min\left(4.0, z^* + \sum \Delta_{\text{spec}}\right)\right)$$

| Hardware / Option | Applied Offset ($\Delta_{\text{spec}}$) |
| :--- | :--- |
| **Premium Brand** (Apple, Samsung) | $+0.40$ |
| **Budget Brand** (Poco, Infinix) | $-0.20$ |
| **5G Support** (Yes) | $+0.15$ |
| **Display Panel** (OLED/AMOLED) | $+0.10$ |
| **Display Resolution** (QHD+/4K) | $+0.25$ |
| **Display Resolution** (HD+) | $-0.25$ |
| **Water Resistance** (IP67/IP68) | $+0.15$ |
| **Wireless Charging** (Yes) | $+0.15$ |
| **Charging Wattage** ($\ge 67$ W) | $+0.10$ |
| **Release Year** ($\ge 2025$) | $+0.10$ |
| **Release Year** ($\le 2021$) | $-0.10$ |

---

## 3. Frontend Pages & Styling (`style.css`)

The application uses **Vanilla CSS** with a modern **Glassmorphic Design System**:
- **Backgrounds**: Deep, responsive dual-gradient themes supporting a native light/dark toggle.
- **Glassmorphism**: `.glass-card` uses `backdrop-filter: blur(16px) saturate(180%)`, a semi-transparent background (`rgba(255, 255, 255, 0.05)` for dark mode), and a high-contrast border.
- **Micro-Animations**: Keyframes for floating components (`floating-glass-card`), sliding filters, and pulse glow effects on submission buttons.

### 3.1 Homepage (`index.html`)
- **Interactive Holographic Phone Mockup**: Renders a floating abstract representation of a phone on the right-hand panel.
- **Range Sliders**: Interactive input controls for RAM, Storage, CPU, Rear/Front camera, and Battery.
- **Real-Time Client-Side Estimate**: A Javascript listener binds changes on the sliders to dynamically compute an instantaneous price tier prediction using an approximation script before form submission.

### 3.2 Result Page (`predict.html`)
- Displays the final predicted category with a color-coded confidence gauge.
- Lists the step-by-step raw calculation log, separating the centroid fuzzy score from the heuristic adjustments.

### 3.3 Dashboard (`dashboard.html`)
- Processes the 1,200 records inside `mobile_price_dataset.csv`.
- Generates interactive Plotly dashboards:
  1. Price Category distribution chart.
  2. Core hardware metrics averages per price category.
  3. Spec correlation heatmap.
- Supports file uploads for analyzing customized pricing tables.

### 3.4 Deals Finder (`deals.html`)
- Catalog of **37 popular devices** across budget, mid-range, premium, and flagship levels.
- Presents brand-new pricing alongside verified refurbished rates from Cashify/Amazon Renewed.
- Integrates client-side brand and category filter buttons with smooth transitions.

---

## 4. Academic Project Report Compiling

- `generate_docx.py` parses the contents of the Markdown report and compiles a professional Microsoft Word file `Mobile_Price_Prediction_Project_Report.docx`.
- Sets up standard **1.2-inch left margins**, **Times New Roman** body fonts (11 pt), centered equations, and custom styled tables containing cell padding and deep purple headers.

---

## 5. Local Setup & Execution

To run this application locally, use the following commands:

```powershell
# Create Virtual Environment
python -m venv venv

# Activate Virtual Environment
.\venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Start Flask Development Server
python app.py
```
The application will run on `http://127.0.0.1:5000/`.
