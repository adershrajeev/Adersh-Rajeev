"""
============================================================
  FUZZY LOGIC MODEL - Mobile Price Prediction System
============================================================
  This module implements a Fuzzy Inference System (FIS)
  to predict mobile phone price categories based on
  specifications like RAM, Battery, Camera, Storage,
  and Processor Speed.

  Instead of traditional ML (Random Forest, SVM, etc.),
  we use FUZZY LOGIC — a form of reasoning that handles
  "degrees of truth" rather than strict True/False.

  Libraries used:
    - skfuzzy: For creating fuzzy sets and rules
    - numpy:   For numerical operations
============================================================
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# =========================================================
#  STEP 1: Define Fuzzy Variables (Antecedents & Consequent)
# =========================================================

def build_fuzzy_system():
    """
    Build the complete Fuzzy Inference System.

    This function:
      1. Creates fuzzy input variables (antecedents)
      2. Creates the fuzzy output variable (consequent)
      3. Defines membership functions for each variable
      4. Defines fuzzy rules
      5. Returns a ControlSystem and Simulation object

    Returns
    -------
    ctrl.ControlSystemSimulation
        A simulation object ready to accept inputs and compute output.
    """

    # ---------------------------------------------------------
    #  ANTECEDENTS (Input Variables)
    #  These are what the user provides — mobile specifications
    # ---------------------------------------------------------

    # RAM (in GB): Range 1 to 18
    ram = ctrl.Antecedent(np.arange(1, 19, 1), 'ram')

    # Battery Power (in mAh): Range 2000 to 7000
    battery = ctrl.Antecedent(np.arange(2000, 7001, 100), 'battery')

    # Rear Camera (in MP): Range 5 to 200
    rear_camera = ctrl.Antecedent(np.arange(5, 201, 1), 'rear_camera')

    # Front Camera (in MP): Range 5 to 64
    front_camera = ctrl.Antecedent(np.arange(5, 65, 1), 'front_camera')

    # Storage (in GB): Range 16 to 512
    storage = ctrl.Antecedent(np.arange(16, 513, 1), 'storage')

    # Processor Speed (in GHz × 10, i.e., 10 = 1.0 GHz): Range 10 to 40
    processor = ctrl.Antecedent(np.arange(10, 41, 1), 'processor')

    # ---------------------------------------------------------
    #  CONSEQUENT (Output Variable)
    #  This is what the system predicts — price category
    #  Mapping: 1=Budget, 2=Mid-Range, 3=Premium, 4=Flagship
    # ---------------------------------------------------------
    price = ctrl.Consequent(np.arange(1, 5, 0.1), 'price')

    # =========================================================
    #  STEP 2: Define Membership Functions
    # =========================================================
    # Membership functions define HOW MUCH a value belongs to
    # a category. We use triangular (trimf) and trapezoidal
    # (trapmf) functions for simplicity.

    # --- RAM Membership ---
    ram['low'] = fuzz.trapmf(ram.universe, [1, 1, 3, 5])
    ram['medium'] = fuzz.trimf(ram.universe, [4, 7, 10])
    ram['high'] = fuzz.trapmf(ram.universe, [8, 12, 18, 18])

    # --- Battery Membership ---
    battery['weak'] = fuzz.trapmf(battery.universe, [2000, 2000, 3000, 4000])
    battery['average'] = fuzz.trimf(battery.universe, [3500, 4500, 5500])
    battery['strong'] = fuzz.trapmf(battery.universe, [5000, 5500, 7000, 7000])

    # --- Rear Camera Membership ---
    rear_camera['basic'] = fuzz.trapmf(rear_camera.universe, [5, 5, 12, 25])
    rear_camera['good'] = fuzz.trimf(rear_camera.universe, [20, 48, 80])
    rear_camera['excellent'] = fuzz.trapmf(rear_camera.universe, [64, 108, 200, 200])

    # --- Front Camera Membership ---
    front_camera['basic'] = fuzz.trapmf(front_camera.universe, [5, 5, 8, 12])
    front_camera['good'] = fuzz.trimf(front_camera.universe, [10, 16, 32])
    front_camera['excellent'] = fuzz.trapmf(front_camera.universe, [24, 32, 64, 64])

    # --- Storage Membership ---
    storage['small'] = fuzz.trapmf(storage.universe, [16, 16, 32, 80])
    storage['medium'] = fuzz.trimf(storage.universe, [64, 128, 256])
    storage['large'] = fuzz.trapmf(storage.universe, [200, 300, 512, 512])

    # --- Processor Membership (values are GHz × 10) ---
    processor['slow'] = fuzz.trapmf(processor.universe, [10, 10, 15, 22])
    processor['moderate'] = fuzz.trimf(processor.universe, [18, 24, 30])
    processor['fast'] = fuzz.trapmf(processor.universe, [27, 32, 40, 40])

    # --- Price Category Membership (Output) ---
    price['budget'] = fuzz.trapmf(price.universe, [1, 1, 1.5, 2.2])
    price['midrange'] = fuzz.trimf(price.universe, [1.8, 2.5, 3.2])
    price['premium'] = fuzz.trimf(price.universe, [2.8, 3.3, 3.8])
    price['flagship'] = fuzz.trapmf(price.universe, [3.5, 3.8, 4, 4])

    # =========================================================
    #  STEP 3: Define Fuzzy Rules
    # =========================================================
    # Rules encode expert knowledge about price categorization.
    # Each rule says: IF (conditions) THEN (price category).

    rules = []

    # --- BUDGET Rules ---
    rules.append(ctrl.Rule(ram['low'] & rear_camera['basic'] & front_camera['basic'], price['budget']))
    rules.append(ctrl.Rule(ram['low'] & storage['small'], price['budget']))
    rules.append(ctrl.Rule(ram['low'] & processor['slow'], price['budget']))
    rules.append(ctrl.Rule(battery['weak'] & rear_camera['basic'] & storage['small'], price['budget']))
    rules.append(ctrl.Rule(ram['low'] & battery['weak'], price['budget']))

    # --- MID-RANGE Rules ---
    rules.append(ctrl.Rule(ram['medium'] & rear_camera['good'] & front_camera['good'], price['midrange']))
    rules.append(ctrl.Rule(ram['medium'] & storage['medium'], price['midrange']))
    rules.append(ctrl.Rule(ram['medium'] & processor['moderate'], price['midrange']))
    rules.append(ctrl.Rule(battery['average'] & rear_camera['good'], price['midrange']))
    rules.append(ctrl.Rule(ram['medium'] & battery['average'] & storage['medium'], price['midrange']))

    # --- PREMIUM Rules ---
    rules.append(ctrl.Rule(ram['high'] & rear_camera['excellent'] & front_camera['excellent'], price['premium']))
    rules.append(ctrl.Rule(ram['high'] & storage['large'], price['premium']))
    rules.append(ctrl.Rule(ram['high'] & processor['fast'] & rear_camera['good'], price['premium']))
    rules.append(ctrl.Rule(battery['strong'] & rear_camera['excellent'], price['premium']))
    rules.append(ctrl.Rule(ram['high'] & processor['moderate'] & rear_camera['excellent'], price['premium']))

    # --- FLAGSHIP Rules ---
    rules.append(ctrl.Rule(ram['high'] & processor['fast'] & rear_camera['excellent'] & front_camera['excellent'], price['flagship']))
    rules.append(ctrl.Rule(ram['high'] & battery['strong'] & storage['large'], price['flagship']))
    rules.append(ctrl.Rule(ram['high'] & processor['fast'] & storage['large'] & rear_camera['excellent'], price['flagship']))
    rules.append(ctrl.Rule(battery['strong'] & processor['fast'] & rear_camera['excellent'] & storage['large'], price['flagship']))
    rules.append(ctrl.Rule(ram['high'] & battery['strong'] & processor['fast'], price['flagship']))

    # =========================================================
    #  STEP 4: Build the Control System
    # =========================================================
    price_ctrl = ctrl.ControlSystem(rules)
    price_sim = ctrl.ControlSystemSimulation(price_ctrl)

    return price_sim


# =========================================================
#  GLOBAL: Build the fuzzy system once when module loads
# =========================================================
_fuzzy_sim = None


def get_fuzzy_system():
    """
    Lazy-load the fuzzy system (build it only once).
    This avoids rebuilding the system on every prediction call.
    """
    global _fuzzy_sim
    if _fuzzy_sim is None:
        _fuzzy_sim = build_fuzzy_system()
    return _fuzzy_sim


# =========================================================
#  STEP 5: Prediction Function
# =========================================================

def predict_price(ram, battery, storage, rear_camera, front_camera, processor):
    """
    Predict the mobile phone's price category using fuzzy logic.

    Parameters
    ----------
    ram : float
        RAM in GB (e.g., 4, 8, 12)
    battery : float
        Battery power in mAh (e.g., 4000, 5000)
    storage : float
        Internal storage in GB (e.g., 64, 128, 256)
    rear_camera : float
        Rear camera resolution in MP (e.g., 12, 48, 108)
    front_camera : float
        Front camera resolution in MP (e.g., 8, 16, 32)
    processor : float
        Processor speed in GHz (e.g., 2.0, 2.8, 3.2)

    Returns
    -------
    dict
        Contains: category, confidence, price_range, raw_score
    """

    # Get (or build) the fuzzy inference system
    sim = build_fuzzy_system()

    # --- Feed inputs into the fuzzy system ---
    # Clamp values to valid ranges to prevent errors
    sim.input['ram'] = max(1, min(18, float(ram)))
    sim.input['battery'] = max(2000, min(7000, float(battery)))
    sim.input['rear_camera'] = max(5, min(200, float(rear_camera)))
    sim.input['front_camera'] = max(5, min(64, float(front_camera)))
    sim.input['storage'] = max(16, min(512, float(storage)))
    sim.input['processor'] = max(10, min(40, float(processor) * 10))  # Convert GHz to GHz×10

    # --- Compute the fuzzy output ---
    try:
        sim.compute()
        raw_score = sim.output['price']
    except Exception as e:
        # If fuzzy computation fails (e.g., no rule fires), return a default
        print(f"⚠️ Fuzzy computation error: {e}")
        raw_score = 2.0  # Default to mid-range

    # --- Map the raw score to a category ---
    if raw_score < 1.8:
        category = 'Budget Phone'
        price_range = '₹6,000 - ₹12,000'
        confidence = max(60, min(98, 100 - abs(raw_score - 1.25) * 40))
    elif raw_score < 2.7:
        category = 'Mid-Range Phone'
        price_range = '₹12,000 - ₹25,000'
        confidence = max(60, min(98, 100 - abs(raw_score - 2.5) * 30))
    elif raw_score < 3.5:
        category = 'Premium Phone'
        price_range = '₹25,000 - ₹50,000'
        confidence = max(60, min(98, 100 - abs(raw_score - 3.3) * 30))
    else:
        category = 'Flagship Phone'
        price_range = '₹50,000 - ₹1,50,000'
        confidence = max(60, min(98, 100 - abs(raw_score - 3.9) * 30))

    # Round confidence to 1 decimal place
    confidence = round(confidence, 1)

    return {
        'category': category,
        'confidence': confidence,
        'price_range': price_range,
        'raw_score': round(raw_score, 2)
    }


# =========================================================
#  Quick Test (run this file directly to test)
# =========================================================
if __name__ == '__main__':
    print("🧪 Testing Fuzzy Model...\n")

    # Test 1: Budget phone
    result = predict_price(ram=3, battery=3500, storage=32, rear_camera=13, front_camera=8, processor=1.6)
    print(f"Test 1 (Budget):   {result}")

    # Test 2: Mid-range phone
    result = predict_price(ram=6, battery=4500, storage=128, rear_camera=48, front_camera=16, processor=2.2)
    print(f"Test 2 (Mid):      {result}")

    # Test 3: Premium phone
    result = predict_price(ram=10, battery=5000, storage=256, rear_camera=108, front_camera=32, processor=2.8)
    print(f"Test 3 (Premium):  {result}")

    # Test 4: Flagship phone
    result = predict_price(ram=16, battery=5500, storage=512, rear_camera=200, front_camera=40, processor=3.4)
    print(f"Test 4 (Flagship): {result}")
