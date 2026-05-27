# 📱 Mobile Price Prediction System using Fuzzy Logic

A modern mini web application that predicts mobile phone price categories using a **Fuzzy Inference System (FIS)**. Built as a BCA/Data Science mini project with a professional, production-style UI.

---

## 🎯 Project Overview

This system accepts mobile phone specifications (RAM, Battery, Camera, Storage, Processor Speed, etc.) from the user and predicts the price category using **Fuzzy Logic** — a form of reasoning that handles "degrees of truth" rather than strict True/False.

### Price Categories
| Category | Price Range |
|---|---|
| 🟢 Budget Phone | ₹6,000 - ₹12,000 |
| 🔵 Mid-Range Phone | ₹12,000 - ₹25,000 |
| 🟣 Premium Phone | ₹25,000 - ₹50,000 |
| 🟡 Flagship Phone | ₹50,000 - ₹1,50,000 |

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Data Science | Pandas, NumPy, Scikit-learn |
| Fuzzy Logic | scikit-fuzzy |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 |
| Charts | Chart.js |
| Icons | Font Awesome 6 |

---

## 📁 Project Structure

```
MobilePricePrediction/
├── app.py                      # Flask backend server
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── mobile_price_dataset.csv    # Auto-generated dataset (1200 records)
├── static/
│   ├── css/style.css           # Custom stylesheet (dark/light theme)
│   ├── js/main.js              # Frontend JavaScript
│   └── images/                 # Static images
├── templates/
│   ├── index.html              # Home page
│   ├── predict.html            # Prediction form
│   ├── dashboard.html          # Dataset analysis dashboard
│   └── result.html             # Prediction result display
├── models/
│   ├── __init__.py
│   └── fuzzy_model.py          # Fuzzy Inference System
└── dataset/
    ├── __init__.py
    └── data_generator.py       # Dataset generation script
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Navigate to the project directory
```bash
cd MobilePricePrediction
```

### Step 2: Create a virtual environment (recommended)
```bash
python -m venv venv
```

### Step 3: Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Step 4: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the application
```bash
python app.py
```

### Step 6: Open in browser
Navigate to: **http://127.0.0.1:5000**

> **Note:** The dataset is automatically generated on the first run. You don't need to run the data generator separately.

---

## 🧠 How Fuzzy Logic Works in This Project

### 1. Fuzzy Variables (Inputs)
| Variable | Membership Functions |
|---|---|
| RAM | Low / Medium / High |
| Battery | Weak / Average / Strong |
| Camera | Basic / Good / Excellent |
| Storage | Small / Medium / Large |
| Processor | Slow / Moderate / Fast |

### 2. Fuzzy Output
- **Price Category**: Budget / Mid-Range / Premium / Flagship

### 3. Example Rules
- IF RAM is **High** AND Camera is **Excellent** → Price is **Premium**
- IF RAM is **Low** AND Storage is **Small** → Price is **Budget**
- IF Battery is **Strong** AND Processor is **Fast** → Price is **Flagship**

### 4. Defuzzification
The system uses the **centroid method** to convert fuzzy output into a crisp numeric score, which is then mapped to a price category.

---

## 📊 Features

### Home Page
- Project introduction and overview
- Feature cards explaining the 3-step process
- Technology stack showcase
- Price category overview

### Prediction Page
- 9-field input form with validation
- Tooltip explanations for each field
- Quick presets (Budget, Mid-Range, Premium, Flagship)
- Loading animation during prediction

### Result Page
- Animated confidence ring
- Color-coded category display
- Input specifications summary
- PDF export functionality
- Prediction history modal

### Dashboard
- Summary statistics cards
- Doughnut chart (category distribution)
- Grouped bar chart (feature averages)
- Radar chart (category comparison)
- Correlation heatmap
- CSV upload for dataset replacement

### Additional Features
- 🌓 Dark/Light theme toggle
- 📱 Fully responsive (mobile-friendly)
- 📄 PDF export of results
- 📜 Prediction history tracking
- ✅ Input validation & error handling
- 💡 Tooltip explanations

---

## 📝 Viva / Presentation Tips

1. **What is Fuzzy Logic?**
   - A form of reasoning that deals with "degrees of truth" rather than strict True/False.
   - Example: RAM of 6 GB is "somewhat medium" and "somewhat high" — fuzzy logic handles this partial membership.

2. **Why Fuzzy Logic instead of ML?**
   - No training data needed for inference
   - Human-readable rules (interpretable)
   - Works well for classification with linguistic variables

3. **Key Libraries:**
   - `scikit-fuzzy` — For creating fuzzy sets, rules, and inference
   - `Flask` — Lightweight Python web framework
   - `Chart.js` — Interactive JavaScript charting library

4. **Membership Functions:**
   - We use triangular (`trimf`) and trapezoidal (`trapmf`) functions
   - They define how much a value "belongs" to a fuzzy set

---

## 📋 Requirements

```
flask==3.1.1
pandas==2.2.3
numpy==1.26.4
matplotlib==3.9.4
seaborn==0.13.2
plotly==5.24.1
scikit-learn==1.6.1
scikit-fuzzy==0.5.0
```

---

## 👨‍🎓 Created For

BCA / Data Science Mini Project  
Subject: Data Science / Artificial Intelligence

---

## 📜 License

This project is created for educational purposes. Feel free to use, modify, and share.
