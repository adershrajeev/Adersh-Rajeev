"""
============================================================
  DATASET GENERATOR - Mobile Price Prediction System
============================================================
  This script generates a synthetic, realistic dataset
  of 1,200 mobile phone specifications across 4 price
  categories: Budget, Mid-Range, Premium, Flagship.

  Each record simulates real-world specs from brands like
  Samsung, Xiaomi, Apple, Vivo, Oppo, Realme, Motorola.

  Usage: Run this file directly to create the CSV.
    $ python data_generator.py
============================================================
"""

import pandas as pd
import numpy as np
import os

# ---------------------
# Set random seed for reproducibility (so results are the same each run)
# ---------------------
np.random.seed(42)

# ---------------------
# Configuration
# ---------------------
NUM_RECORDS = 1200  # Total number of records to generate
RECORDS_PER_CATEGORY = NUM_RECORDS // 4  # 300 records per category (balanced)

# Brand levels:  1 = Budget brand,  2 = Mid brand,  3 = Premium brand
BRAND_MAPPING = {
    'Xiaomi': 1, 'Realme': 1, 'Motorola': 1,
    'Vivo': 2, 'Oppo': 2, 'Samsung': 2,
    'Apple': 3, 'OnePlus': 3
}


def generate_category(category_name, n, specs):
    """
    Generate `n` records for a given price category.

    Parameters
    ----------
    category_name : str
        One of 'Budget Phone', 'Mid-Range Phone', 'Premium Phone', 'Flagship Phone'
    n : int
        Number of records to generate
    specs : dict
        Dictionary with (low, high) ranges for each feature

    Returns
    -------
    pd.DataFrame
        DataFrame with all columns filled in for this category
    """
    data = {
        # RAM in GB — e.g., Budget phones get 2-4 GB, Flagship get 12-16 GB
        'ram': np.random.randint(specs['ram'][0], specs['ram'][1] + 1, n),

        # Battery capacity in mAh
        'battery_power': np.random.randint(specs['battery'][0], specs['battery'][1] + 1, n),

        # Internal storage in GB
        'storage': np.random.choice(specs['storage'], n),

        # Rear camera resolution in megapixels
        'rear_camera_mp': np.random.randint(specs['rear_camera'][0], specs['rear_camera'][1] + 1, n),

        # Front camera resolution in megapixels
        'front_camera_mp': np.random.randint(specs['front_camera'][0], specs['front_camera'][1] + 1, n),

        # Screen size in inches (uniform float)
        'screen_size': np.round(np.random.uniform(specs['screen'][0], specs['screen'][1], n), 1),

        # Processor speed in GHz (uniform float)
        'processor_speed': np.round(np.random.uniform(specs['processor'][0], specs['processor'][1], n), 1),

        # Refresh rate in Hz — common values: 60, 90, 120, 144
        'refresh_rate': np.random.choice(specs['refresh_rate'], n),

        # Whether the phone supports 5G (0 = No, 1 = Yes)
        'has_5g': np.random.choice(specs['has_5g'], n, p=specs['5g_prob']),

        # Brand level: 1 (budget), 2 (mid), 3 (premium)
        'brand_level': np.random.choice(specs['brand_levels'], n, p=specs['brand_prob']),

        # Target label
        'price_category': category_name
    }
    return pd.DataFrame(data)


def main():
    """
    Main function — defines spec ranges per category and generates full dataset.
    """

    # --- BUDGET PHONE specs ---
    budget_specs = {
        'ram': (2, 4),
        'battery': (3000, 4500),
        'storage': [32, 64],
        'rear_camera': (8, 16),
        'front_camera': (5, 8),
        'screen': (5.5, 6.2),
        'processor': (1.4, 2.0),
        'refresh_rate': [60],
        'has_5g': [0, 1],
        '5g_prob': [0.9, 0.1],
        'brand_levels': [1, 2],
        'brand_prob': [0.75, 0.25]
    }

    # --- MID-RANGE PHONE specs ---
    midrange_specs = {
        'ram': (4, 8),
        'battery': (4000, 5500),
        'storage': [64, 128],
        'rear_camera': (16, 64),
        'front_camera': (8, 16),
        'screen': (6.0, 6.6),
        'processor': (2.0, 2.6),
        'refresh_rate': [60, 90],
        'has_5g': [0, 1],
        '5g_prob': [0.5, 0.5],
        'brand_levels': [1, 2],
        'brand_prob': [0.4, 0.6]
    }

    # --- PREMIUM PHONE specs ---
    premium_specs = {
        'ram': (8, 12),
        'battery': (4500, 5500),
        'storage': [128, 256],
        'rear_camera': (48, 108),
        'front_camera': (16, 32),
        'screen': (6.4, 6.8),
        'processor': (2.6, 3.2),
        'refresh_rate': [90, 120],
        'has_5g': [0, 1],
        '5g_prob': [0.2, 0.8],
        'brand_levels': [2, 3],
        'brand_prob': [0.45, 0.55]
    }

    # --- FLAGSHIP PHONE specs ---
    flagship_specs = {
        'ram': (12, 16),
        'battery': (4800, 6000),
        'storage': [256, 512],
        'rear_camera': (64, 200),
        'front_camera': (32, 60),
        'screen': (6.5, 7.0),
        'processor': (3.0, 3.6),
        'refresh_rate': [120, 144],
        'has_5g': [1],
        '5g_prob': [1.0],
        'brand_levels': [2, 3],
        'brand_prob': [0.3, 0.7]
    }

    # --- Generate data for each category ---
    print("📊 Generating dataset...")
    budget_df = generate_category('Budget Phone', RECORDS_PER_CATEGORY, budget_specs)
    midrange_df = generate_category('Mid-Range Phone', RECORDS_PER_CATEGORY, midrange_specs)
    premium_df = generate_category('Premium Phone', RECORDS_PER_CATEGORY, premium_specs)
    flagship_df = generate_category('Flagship Phone', RECORDS_PER_CATEGORY, flagship_specs)

    # --- Combine all categories into one DataFrame ---
    full_dataset = pd.concat(
        [budget_df, midrange_df, premium_df, flagship_df],
        ignore_index=True  # Reset index so it goes 0, 1, 2, ...
    )

    # --- Shuffle the dataset (so it's not ordered by category) ---
    full_dataset = full_dataset.sample(frac=1, random_state=42).reset_index(drop=True)

    # --- Save to CSV ---
    # Save in the project root (one level up from dataset/)
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mobile_price_dataset.csv')
    full_dataset.to_csv(output_path, index=False)
    print(f"✅ Dataset saved to: {output_path}")
    print(f"   Total records: {len(full_dataset)}")
    print(f"   Columns: {list(full_dataset.columns)}")
    print(f"\n   Category Distribution:")
    print(full_dataset['price_category'].value_counts().to_string())

    return full_dataset


# --- Run the script ---
if __name__ == '__main__':
    main()
