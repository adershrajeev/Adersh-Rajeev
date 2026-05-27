"""
============================================================
  FLASK APPLICATION - Mobile Price Prediction System
============================================================
  This is the main backend server. It handles:
    - Page routing (Home, Predict, Dashboard, Result)
    - Prediction API endpoint
    - Dataset analysis endpoint
    - CSV file upload
    - Prediction history management

  Run this file to start the server:
    $ python app.py
============================================================
"""

import os
import json
import csv
from datetime import datetime

from flask import (
    Flask, render_template, request,
    jsonify, redirect, url_for, session, flash
)
import pandas as pd
import numpy as np

# Import our custom fuzzy model
from models.fuzzy_model import predict_price

# =========================================================
#  APP CONFIGURATION
# =========================================================
app = Flask(__name__)
app.secret_key = 'mobile_price_fuzzy_2025'  # Required for session & flash messages

# Path to the dataset file
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'mobile_price_dataset.csv')

# Store prediction history in memory (resets on server restart)
prediction_history = []


# =========================================================
#  HELPER: Load Dataset
# =========================================================
def load_dataset():
    """
    Load the mobile price dataset from CSV.
    If the file doesn't exist, generate it first.

    Returns
    -------
    pd.DataFrame or None
    """
    if not os.path.exists(DATASET_PATH):
        # Auto-generate dataset if it doesn't exist
        print("📊 Dataset not found. Generating now...")
        from dataset.data_generator import main as generate_dataset
        generate_dataset()

    if os.path.exists(DATASET_PATH):
        return pd.read_csv(DATASET_PATH)
    return None


# =========================================================
#  ROUTE: Home Page
# =========================================================
@app.route('/')
def home():
    """
    Render the landing / home page.
    Shows project introduction, features, and navigation.
    """
    return render_template('index.html')


# =========================================================
#  ROUTE: Prediction Form
# =========================================================
@app.route('/predict')
def predict_page():
    """
    Render the prediction input form page.
    Users enter mobile specifications here.
    """
    return render_template('predict.html')


# =========================================================
#  ROUTE: Handle Prediction (POST)
# =========================================================
@app.route('/predict', methods=['POST'])
def predict():
    """
    Process the prediction form submission.

    Steps:
      1. Validate all input fields
      2. Pass values to fuzzy model
      3. Store result in prediction history
      4. Render the result page
    """
    try:
        # --- Extract form data ---
        ram = float(request.form.get('ram', 4))
        battery = float(request.form.get('battery_power', 4000))
        storage = float(request.form.get('storage', 64))
        rear_camera = float(request.form.get('rear_camera_mp', 12))
        front_camera = float(request.form.get('front_camera_mp', 8))
        screen_size = float(request.form.get('screen_size', 6.1))
        processor = float(request.form.get('processor_speed', 2.0))
        refresh_rate = int(request.form.get('refresh_rate', 60))
        has_5g = int(request.form.get('has_5g', 0))
        brand_level = int(request.form.get('brand_level', 1))

        # New fields
        release_year = int(request.form.get('release_year', 2025))
        cpu_cores = int(request.form.get('cpu_cores', 8))
        display_type = request.form.get('display_type', 'AMOLED')
        display_resolution = request.form.get('display_resolution', 'Full HD+')
        camera_setup = request.form.get('camera_setup', 'Triple Camera')
        charging_speed = int(request.form.get('charging_speed', 33))
        wireless_charging = int(request.form.get('wireless_charging', 0))
        water_resistance = request.form.get('water_resistance', 'None')
        fingerprint_sensor = request.form.get('fingerprint_sensor', 'Side-Mounted')
        nfc_support = int(request.form.get('nfc_support', 1))
        audio_jack = int(request.form.get('audio_jack', 1))

        # --- Input Validation ---
        errors = []
        if not (1 <= ram <= 18):
            errors.append('RAM must be between 1 and 18 GB.')
        if not (2000 <= battery <= 7000):
            errors.append('Battery must be between 2000 and 7000 mAh.')
        if not (16 <= storage <= 512):
            errors.append('Storage must be between 16 and 512 GB.')
        if not (5 <= rear_camera <= 200):
            errors.append('Rear Camera must be between 5 and 200 MP.')
        if not (5 <= front_camera <= 64):
            errors.append('Front Camera must be between 5 and 64 MP.')
        if not (1.0 <= processor <= 4.0):
            errors.append('Processor must be between 1.0 and 4.0 GHz.')
        if not (2020 <= release_year <= 2026):
            errors.append('Release Year must be between 2020 and 2026.')
        if not (5 <= charging_speed <= 240):
            errors.append('Charging Speed must be between 5 and 240 W.')

        if errors:
            flash(' | '.join(errors), 'danger')
            return redirect(url_for('predict_page'))

        # --- Run Fuzzy Prediction ---
        result = predict_price(
            ram=ram,
            battery=battery,
            storage=storage,
            rear_camera=rear_camera,
            front_camera=front_camera,
            processor=processor
        )

        raw_score = result['raw_score']

        # --- Heuristic Adjustments based on new premium features ---
        adj = 0.0
        
        # 1. Brand Tier
        if brand_level == 3:  # Premium
            adj += 0.4
        elif brand_level == 1:  # Budget
            adj -= 0.2
            
        # 2. 5G Support
        if has_5g == 1:
            adj += 0.15
            
        # 3. Display Resolution
        if display_resolution == 'Quad HD+':
            adj += 0.25
        elif display_resolution == 'HD+':
            adj -= 0.25
            
        # 4. Display Type
        if display_type in ['AMOLED', 'OLED']:
            adj += 0.1
            
        # 5. Water Resistance
        if water_resistance in ['IP67', 'IP68']:
            adj += 0.15
        elif water_resistance == 'IP53':
            adj += 0.05
            
        # 6. Wireless Charging
        if wireless_charging == 1:
            adj += 0.15
            
        # 7. Release Year
        if release_year >= 2025:
            adj += 0.1
        elif release_year <= 2021:
            adj -= 0.1
            
        # 8. Charging Speed
        if charging_speed >= 67:
            adj += 0.1
            
        # Apply adjustment and clamp score between 1.0 and 4.0
        final_score = max(1.0, min(4.0, raw_score + adj))

        # --- Map final_score to Category, Price Range, and Confidence ---
        if final_score < 1.8:
            category = 'Budget Phone'
            price_range = '₹6,000 - ₹12,000'
            confidence = max(60, min(98, 100 - abs(final_score - 1.25) * 40))
        elif final_score < 2.7:
            category = 'Mid-Range Phone'
            price_range = '₹12,000 - ₹25,000'
            confidence = max(60, min(98, 100 - abs(final_score - 2.5) * 30))
        elif final_score < 3.5:
            category = 'Premium Phone'
            price_range = '₹25,000 - ₹50,000'
            confidence = max(60, min(98, 100 - abs(final_score - 3.3) * 30))
        else:
            category = 'Flagship Phone'
            price_range = '₹50,000 - ₹1,50,000'
            confidence = max(60, min(98, 100 - abs(final_score - 3.9) * 30))

        confidence = round(confidence, 1)

        # --- Compute dynamic pricing based on final_score ---
        if final_score < 1.8:
            base_price = 6000 + (final_score - 1.0) / 0.8 * 6000
        elif final_score < 2.7:
            base_price = 12000 + (final_score - 1.8) / 0.9 * 13000
        elif final_score < 3.5:
            base_price = 25000 + (final_score - 2.7) / 0.8 * 25000
        else:
            base_price = 50000 + (final_score - 3.5) / 0.5 * 80000
            
        base_price = int(round(base_price, -2)) # round to nearest 100

        # Define variant sizes
        variant1_ram = int(ram)
        variant1_storage = int(storage)
        
        variant2_ram = int(ram)
        variant2_storage = int(storage * 2) if storage < 512 else 512
        if variant2_storage == variant1_storage:
            variant2_ram = int(ram * 1.5) if ram < 18 else 18
            
        price_var1 = base_price
        price_var2 = int(base_price * 1.15)
        price_var2 = int(round(price_var2, -2))
        
        retailer_deals = [
            {'variant': f'{variant1_storage}GB {variant1_ram}GB RAM', 'price': f'₹{price_var1:,}', 'site': 'amazon.in', 'link': 'https://amazon.in', 'color': '#ff9900'},
            {'variant': f'{variant1_storage}GB {variant1_ram}GB RAM', 'price': f'₹{price_var1 - 250:,}', 'site': 'flipkart.com', 'link': 'https://flipkart.com', 'color': '#2874f0'},
            {'variant': f'{variant2_storage}GB {variant2_ram}GB RAM', 'price': f'₹{price_var2:,}', 'site': 'amazon.in', 'link': 'https://amazon.in', 'color': '#ff9900'},
            {'variant': f'{variant2_storage}GB {variant2_ram}GB RAM', 'price': f'₹{price_var2 - 300:,}', 'site': 'flipkart.com', 'link': 'https://flipkart.com', 'color': '#2874f0'}
        ]

        if category == 'Budget Phone':
            competitors = [
                {'name': 'Redmi 13C', 'price': '₹9,999', 'icon': 'fa-mobile-alt', 'color': '#ff4a00'},
                {'name': 'Realme C65', 'price': '₹10,499', 'icon': 'fa-mobile-alt', 'color': '#ffcc00'},
                {'name': 'Moto G34 5G', 'price': '₹10,999', 'icon': 'fa-mobile-alt', 'color': '#0099ff'},
                {'name': 'Samsung Galaxy M14', 'price': '₹11,499', 'icon': 'fa-mobile-alt', 'color': '#0c4da2'}
            ]
        elif category == 'Mid-Range Phone':
            competitors = [
                {'name': 'OnePlus Nord CE4 Lite', 'price': '₹19,999', 'icon': 'fa-mobile-alt', 'color': '#eb0029'},
                {'name': 'Vivo T3 5G', 'price': '₹19,999', 'icon': 'fa-mobile-alt', 'color': '#0054ff'},
                {'name': 'Realme 12 Pro', 'price': '₹23,999', 'icon': 'fa-mobile-alt', 'color': '#ffcc00'},
                {'name': 'Samsung Galaxy F55', 'price': '₹22,999', 'icon': 'fa-mobile-alt', 'color': '#0c4da2'}
            ]
        elif category == 'Premium Phone':
            competitors = [
                {'name': 'OnePlus 12R', 'price': '₹39,999', 'icon': 'fa-mobile-alt', 'color': '#eb0029'},
                {'name': 'Nothing Phone (2)', 'price': '₹36,999', 'icon': 'fa-mobile-alt', 'color': '#a855f7'},
                {'name': 'iQOO Neo9 Pro', 'price': '₹35,999', 'icon': 'fa-mobile-alt', 'color': '#ff3300'},
                {'name': 'Samsung Galaxy S23 FE', 'price': '₹42,999', 'icon': 'fa-mobile-alt', 'color': '#0c4da2'}
            ]
        else:
            competitors = [
                {'name': 'Apple iPhone 16 Plus', 'price': '₹79,900', 'icon': 'fa-mobile-alt', 'color': '#ff33aa'},
                {'name': 'Samsung Galaxy S24 Ultra', 'price': '₹1,29,999', 'icon': 'fa-mobile-alt', 'color': '#0c4da2'},
                {'name': 'OnePlus 12', 'price': '₹64,999', 'icon': 'fa-mobile-alt', 'color': '#eb0029'},
                {'name': 'Google Pixel 9 Pro XL', 'price': '₹1,09,999', 'icon': 'fa-mobile-alt', 'color': '#4285f4'}
            ]

        # --- Build result data for template ---
        prediction_data = {
            'category': category,
            'confidence': confidence,
            'price_range': price_range,
            'raw_score': round(final_score, 2),
            'inputs': {
                'Brand Tier': ['Budget', 'Mid-Tier', 'Premium'][brand_level - 1],
                'Release Year': f'{release_year}',
                '5G Support': 'Yes' if has_5g else 'No',
                'RAM': f'{ram} GB',
                'Storage': f'{int(storage)} GB',
                'Processor': f'{processor} GHz ({cpu_cores}-Core)',
                'Screen Size': f'{screen_size}"',
                'Refresh Rate': f'{refresh_rate} Hz',
                'Display Type': f'{display_type} ({display_resolution})',
                'Rear Camera': f'{int(rear_camera)} MP ({camera_setup})',
                'Front Camera': f'{int(front_camera)} MP',
                'Battery': f'{int(battery)} mAh',
                'Charging Speed': f'{charging_speed}W' + (' + Wireless' if wireless_charging else ''),
                'IP Rating': f'{water_resistance}',
                'Fingerprint': f'{fingerprint_sensor}',
                'NFC Support': 'Yes' if nfc_support else 'No',
                '3.5mm Jack': 'Yes' if audio_jack else 'No'
            },
            'deals': retailer_deals,
            'competitors': competitors,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # --- Store in history ---
        prediction_history.insert(0, prediction_data)
        # Keep only the last 50 predictions
        if len(prediction_history) > 50:
            prediction_history.pop()

        return render_template('result.html', prediction=prediction_data)

    except ValueError as e:
        flash(f'Invalid input: Please enter valid numbers. ({str(e)})', 'danger')
        return redirect(url_for('predict_page'))
    except Exception as e:
        flash(f'Prediction error: {str(e)}', 'danger')
        return redirect(url_for('predict_page'))


# =========================================================
#  ROUTE: Dashboard / Analysis Page
# =========================================================
@app.route('/dashboard')
def dashboard():
    """
    Render the dataset analysis dashboard page.
    """
    return render_template('dashboard.html')


# =========================================================
#  API: Get Dataset Analysis Data (JSON)
# =========================================================
@app.route('/api/analysis')
def analysis_data():
    """
    Return dataset statistics as JSON for frontend charts.

    Provides:
      - Category distribution (for pie chart)
      - Feature averages per category (for bar charts)
      - Correlation matrix (for heatmap)
      - Summary statistics
    """
    df = load_dataset()
    if df is None:
        return jsonify({'error': 'Dataset not found'}), 404

    # --- Category Distribution ---
    cat_dist = df['price_category'].value_counts().to_dict()

    # --- Feature Averages by Category ---
    features = ['ram', 'battery_power', 'storage', 'rear_camera_mp', 'front_camera_mp', 'processor_speed', 'refresh_rate']
    avg_by_cat = {}
    for cat in df['price_category'].unique():
        cat_data = df[df['price_category'] == cat]
        avg_by_cat[cat] = {feat: round(cat_data[feat].mean(), 1) for feat in features}

    # --- Correlation Matrix (numeric columns only) ---
    numeric_cols = ['ram', 'battery_power', 'storage', 'rear_camera_mp', 'front_camera_mp',
                    'screen_size', 'processor_speed', 'refresh_rate',
                    'has_5g', 'brand_level']
    corr = df[numeric_cols].corr().round(2).to_dict()

    # --- Summary Statistics ---
    summary = {
        'total_records': len(df),
        'num_features': len(df.columns),
        'categories': list(df['price_category'].unique()),
        'feature_stats': {}
    }
    for feat in features:
        summary['feature_stats'][feat] = {
            'min': float(df[feat].min()),
            'max': float(df[feat].max()),
            'mean': round(float(df[feat].mean()), 1),
            'std': round(float(df[feat].std()), 1)
        }

    return jsonify({
        'category_distribution': cat_dist,
        'avg_by_category': avg_by_cat,
        'correlation': corr,
        'summary': summary
    })


# =========================================================
#  API: Get Prediction History (JSON)
# =========================================================
@app.route('/api/history')
def get_history():
    """Return the last 50 predictions as JSON."""
    return jsonify(prediction_history)


# =========================================================
#  ROUTE: Handle CSV Upload
# =========================================================
@app.route('/upload', methods=['POST'])
def upload_csv():
    """
    Accept a CSV file upload for dataset replacement / analysis.
    Saves the uploaded file as the main dataset.
    """
    if 'file' not in request.files:
        flash('No file uploaded.', 'warning')
        return redirect(url_for('dashboard'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'warning')
        return redirect(url_for('dashboard'))

    if not file.filename.endswith('.csv'):
        flash('Only CSV files are accepted.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        file.save(DATASET_PATH)
        flash('Dataset uploaded successfully! Charts will update with new data.', 'success')
    except Exception as e:
        flash(f'Upload failed: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))


# =========================================================
#  ROUTE: Deals & Refurbished (HTML)
# =========================================================
@app.route('/deals')
def deals_page():
    """
    Render the Deals & Refurbished mobile page.
    """
    devices = [
        # Flagship Phone (7 devices)
        {
            'name': 'Apple iPhone 15 Pro Max',
            'brand': 'Apple',
            'category': 'Flagship Phone',
            'specs': '256GB Storage, 8GB RAM, 48MP Triple Camera',
            'new_price': '₹1,39,900',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹99,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Like New',
            'color': '#ff33aa',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Samsung Galaxy S24 Ultra',
            'brand': 'Samsung',
            'category': 'Flagship Phone',
            'specs': '512GB Storage, 12GB RAM, 200MP Quad Camera',
            'new_price': '₹1,24,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹89,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#0c4da2',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Apple iPhone 15 Pro',
            'brand': 'Apple',
            'category': 'Flagship Phone',
            'specs': '128GB Storage, 8GB RAM, 48MP Triple Camera',
            'new_price': '₹1,19,900',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹84,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Like New',
            'color': '#ff33aa',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Google Pixel 8 Pro',
            'brand': 'Google',
            'category': 'Flagship Phone',
            'specs': '128GB Storage, 12GB RAM, 50MP Triple Camera',
            'new_price': '₹93,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹59,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#4285f4',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'OnePlus 12',
            'brand': 'OnePlus',
            'category': 'Flagship Phone',
            'specs': '256GB Storage, 12GB RAM, 50MP Triple Camera',
            'new_price': '₹64,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹46,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Like New',
            'color': '#eb0029',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Xiaomi 14',
            'brand': 'Xiaomi/Redmi',
            'category': 'Flagship Phone',
            'specs': '512GB Storage, 12GB RAM, 50MP Triple Camera',
            'new_price': '₹69,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹49,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Superb',
            'color': '#ff4a00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Xiaomi 13 Pro',
            'brand': 'Xiaomi/Redmi',
            'category': 'Flagship Phone',
            'specs': '256GB Storage, 12GB RAM, 50MP Triple Camera',
            'new_price': '₹74,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹47,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#ff4a00',
            'icon': 'fa-mobile-alt'
        },
        # Premium Phone (8 devices)
        {
            'name': 'Apple iPhone 14 Pro',
            'brand': 'Apple',
            'category': 'Premium Phone',
            'specs': '128GB Storage, 6GB RAM, 48MP Triple Camera',
            'new_price': '₹1,09,900',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹72,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Like New',
            'color': '#ff33aa',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Samsung Galaxy S24+',
            'brand': 'Samsung',
            'category': 'Premium Phone',
            'specs': '256GB Storage, 12GB RAM, 50MP Triple Camera',
            'new_price': '₹99,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹69,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#0c4da2',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Apple iPhone 14',
            'brand': 'Apple',
            'category': 'Premium Phone',
            'specs': '128GB Storage, 6GB RAM, 12MP Dual Camera',
            'new_price': '₹59,900',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹41,999',
            'refurb_site': 'Amazon Renewed',
            'refurb_link': 'https://amazon.in',
            'condition': 'Good',
            'color': '#ff33aa',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Apple iPhone 13',
            'brand': 'Apple',
            'category': 'Premium Phone',
            'specs': '128GB Storage, 4GB RAM, 12MP Dual Camera',
            'new_price': '₹48,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹32,999',
            'refurb_site': 'Amazon Renewed',
            'refurb_link': 'https://amazon.in',
            'condition': 'Good',
            'color': '#ff33aa',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Samsung Galaxy S23',
            'brand': 'Samsung',
            'category': 'Premium Phone',
            'specs': '128GB Storage, 8GB RAM, 50MP Triple Camera',
            'new_price': '₹46,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹34,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#0c4da2',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'OnePlus 12R',
            'brand': 'OnePlus',
            'category': 'Premium Phone',
            'specs': '128GB Storage, 8GB RAM, 50MP Triple Camera',
            'new_price': '₹39,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹29,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Superb',
            'color': '#eb0029',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Nothing Phone (2)',
            'brand': 'Nothing',
            'category': 'Premium Phone',
            'specs': '256GB Storage, 12GB RAM, 50MP Dual Camera',
            'new_price': '₹37,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹27,499',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#a855f7',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Motorola Edge 50 Ultra',
            'brand': 'Motorola',
            'category': 'Premium Phone',
            'specs': '512GB Storage, 16GB RAM, 50MP Triple Camera',
            'new_price': '₹59,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹41,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Like New',
            'color': '#0099ff',
            'icon': 'fa-mobile-alt'
        },
        # Mid-Range Phone (15 devices)
        {
            'name': 'Samsung Galaxy A55 5G',
            'brand': 'Samsung',
            'category': 'Mid-Range Phone',
            'specs': '128GB Storage, 8GB RAM, 50MP Triple Camera',
            'new_price': '₹36,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹24,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Like New',
            'color': '#0c4da2',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Google Pixel 7a',
            'brand': 'Google',
            'category': 'Mid-Range Phone',
            'specs': '128GB Storage, 8GB RAM, 64MP Dual Camera',
            'new_price': '₹34,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹23,999',
            'refurb_site': 'Amazon Renewed',
            'refurb_link': 'https://amazon.in',
            'condition': 'Excellent',
            'color': '#4285f4',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Motorola Edge 50 Pro',
            'brand': 'Motorola',
            'category': 'Mid-Range Phone',
            'specs': '256GB Storage, 8GB RAM, 50MP Triple Camera',
            'new_price': '₹31,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹22,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Superb',
            'color': '#0099ff',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Realme 12 Pro+',
            'brand': 'Realme',
            'category': 'Mid-Range Phone',
            'specs': '128GB Storage, 8GB RAM, 64MP Triple Camera',
            'new_price': '₹29,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹21,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#ffcc00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Realme GT 6',
            'brand': 'Realme',
            'category': 'Mid-Range Phone',
            'specs': '256GB Storage, 12GB RAM, 50MP Triple Camera',
            'new_price': '₹40,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹29,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Like New',
            'color': '#ffcc00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Redmi Note 13 Pro',
            'brand': 'Xiaomi/Redmi',
            'category': 'Mid-Range Phone',
            'specs': '256GB Storage, 8GB RAM, 200MP Triple Camera',
            'new_price': '₹25,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹16,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Good',
            'color': '#ff4a00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'OnePlus Nord CE4',
            'brand': 'OnePlus',
            'category': 'Mid-Range Phone',
            'specs': '128GB Storage, 8GB RAM, 50MP Dual Camera',
            'new_price': '₹24,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹17,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Superb',
            'color': '#eb0029',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Nothing Phone (2a)',
            'brand': 'Nothing',
            'category': 'Mid-Range Phone',
            'specs': '128GB Storage, 8GB RAM, 50MP Dual Camera',
            'new_price': '₹23,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹17,499',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#a855f7',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Nothing Phone (1)',
            'brand': 'Nothing',
            'category': 'Mid-Range Phone',
            'specs': '128GB Storage, 8GB RAM, 50MP Dual Camera',
            'new_price': '₹29,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹18,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Superb',
            'color': '#a855f7',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Poco F6 5G',
            'brand': 'Poco',
            'category': 'Mid-Range Phone',
            'specs': '256GB Storage, 8GB RAM, 50MP Dual Camera',
            'new_price': '₹29,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹21,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#ffcc00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Poco X6 Pro 5G',
            'brand': 'Poco',
            'category': 'Mid-Range Phone',
            'specs': '256GB Storage, 8GB RAM, 64MP Triple Camera',
            'new_price': '₹25,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹18,499',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#ffcc00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Redmi Note 13 5G',
            'brand': 'Xiaomi/Redmi',
            'category': 'Mid-Range Phone',
            'specs': '128GB Storage, 6GB RAM, 108MP Triple Camera',
            'new_price': '₹17,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹12,499',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Good',
            'color': '#ff4a00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Realme Narzo 70 Pro 5G',
            'brand': 'Realme',
            'category': 'Mid-Range Phone',
            'specs': '128GB Storage, 8GB RAM, 50MP Triple Camera',
            'new_price': '₹19,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹13,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Superb',
            'color': '#ffcc00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Samsung Galaxy F54 5G',
            'brand': 'Samsung',
            'category': 'Mid-Range Phone',
            'specs': '256GB Storage, 8GB RAM, 108MP Triple Camera',
            'new_price': '₹22,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹15,499',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#0c4da2',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Moto G84 5G',
            'brand': 'Motorola',
            'category': 'Mid-Range Phone',
            'specs': '256GB Storage, 12GB RAM, 50MP Dual Camera',
            'new_price': '₹18,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹11,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#0099ff',
            'icon': 'fa-mobile-alt'
        },
        # Budget Phone (7 devices)
        {
            'name': 'Realme 12x 5G',
            'brand': 'Realme',
            'category': 'Budget Phone',
            'specs': '128GB Storage, 6GB RAM, 50MP Dual Camera',
            'new_price': '₹11,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹8,499',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Good',
            'color': '#ffcc00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Samsung Galaxy M14',
            'brand': 'Samsung',
            'category': 'Budget Phone',
            'specs': '128GB Storage, 6GB RAM, 50MP Triple Camera',
            'new_price': '₹11,499',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹7,899',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#0c4da2',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Moto G34 5G',
            'brand': 'Motorola',
            'category': 'Budget Phone',
            'specs': '128GB Storage, 8GB RAM, 50MP Dual Camera',
            'new_price': '₹10,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹7,899',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Superb',
            'color': '#0099ff',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Redmi 13C 5G',
            'brand': 'Xiaomi/Redmi',
            'category': 'Budget Phone',
            'specs': '128GB Storage, 6GB RAM, 50MP Dual Camera',
            'new_price': '₹10,499',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹7,299',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#ff4a00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Realme C65',
            'brand': 'Realme',
            'category': 'Budget Phone',
            'specs': '64GB Storage, 4GB RAM, 50MP Dual Camera',
            'new_price': '₹10,499',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹7,499',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Good',
            'color': '#ffcc00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Poco M6 Pro 5G',
            'brand': 'Poco',
            'category': 'Budget Phone',
            'specs': '128GB Storage, 6GB RAM, 50MP Dual Camera',
            'new_price': '₹9,999',
            'new_site': 'Flipkart',
            'new_link': 'https://flipkart.com',
            'refurb_price': '₹6,499',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Excellent',
            'color': '#ffcc00',
            'icon': 'fa-mobile-alt'
        },
        {
            'name': 'Moto G24 Power',
            'brand': 'Motorola',
            'category': 'Budget Phone',
            'specs': '128GB Storage, 4GB RAM, 50MP Dual Camera',
            'new_price': '₹8,999',
            'new_site': 'Amazon.in',
            'new_link': 'https://amazon.in',
            'refurb_price': '₹5,999',
            'refurb_site': 'Cashify',
            'refurb_link': 'https://cashify.in',
            'condition': 'Good',
            'color': '#0099ff',
            'icon': 'fa-mobile-alt'
        }
    ]
    return render_template('deals.html', devices=devices)


# =========================================================
#  START THE SERVER
# =========================================================
if __name__ == '__main__':
    # Auto-generate dataset on first run
    if not os.path.exists(DATASET_PATH):
        print("📊 Generating dataset for first run...")
        from dataset.data_generator import main as generate_dataset
        generate_dataset()

    print("\n🚀 Starting Mobile Price Prediction System...")
    print("   Open: http://127.0.0.1:5000\n")

    # debug=True enables auto-reload during development
    app.run(debug=True, host='0.0.0.0', port=5000)
