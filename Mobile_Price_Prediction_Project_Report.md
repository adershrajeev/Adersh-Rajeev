# PROJECT REPORT
## MOBILE PHONE PRICE CATEGORY PREDICTION SYSTEM USING FUZZY INFERENCE & HEURISTIC MODELS

**A Case Study on Data Analytics and Intelligent Price Estimation**

---

## ABSTRACT

In the contemporary smartphone market, rapid technological advancements and diverse consumer preferences make accurate price category classification a significant challenge. This project develops a **Mobile Phone Price Category Prediction System** utilizing a Mamdani Fuzzy Inference System (FIS) combined with heuristic adjustment rules. By analyzing twenty key hardware specifications, the system classifies smartphones into four distinct price tiers: *Budget Phone*, *Mid-Range Phone*, *Premium Phone*, and *Flagship Phone*.

The application is built on a robust Python/Flask backend and utilizes `scikit-fuzzy` to construct membership functions and evaluate rule bases. To handle premium specifications beyond standard antecedents, a heuristic adjustment subsystem fine-tunes the raw fuzzy output. The user interface features a glassmorphic design system that supports dark/light modes, interactive specification-tuning range sliders, dynamic data analytics dashboards, and a live deals comparison platform featuring brand new prices side-by-side with verified refurbished rates for thirty-seven popular models. 

---

## TABLE OF CONTENTS

* **Abstract** ......................................................................................... ii
* **List of Figures** ................................................................................... v
* **List of Tables** ................................................................................... vi
* **1 Introduction** .................................................................................. 1
  * **1.1 Project Overview & Objectives** ........................................................... 1
  * **1.2 Fuzzy Set Theory & Mamdani Inference** ................................................. 2
    * *Definition 1.1.1 (Fuzzy Set)* ................................................................ 2
    * *Theorem 1.1.2 (Mamdani Max-Min Composition)* .......................................... 2
    * *Proof of Defuzzification Convergence* ....................................................... 3
    * *Defuzzification Formula* ..................................................................... 3
* **2 System Design & Implementation** .............................................................. 4
  * **2.1 Technical Stack & System Flow** ........................................................... 4
  * **2.2 Membership Functions & Heuristics** ..................................................... 5
    * *2.2.1 Antecedent and Consequent Definitions* ............................................. 5
    * *2.2.2 Heuristic Spec Adjustments* ............................................................ 6
* **3 Results, Dashboard & Deals Finder** ........................................................... 7
  * **3.1 Dataset Dashboard Analysis** ................................................................ 7
  * **3.2 Deals & Refurbished Mobile Catalog** ....................................................... 8
* **Bibliography** ..................................................................................... 9

---

## LIST OF FIGURES

* **Figure 1.1**: System Architecture and Dataflow Diagram ................................................ 4
* **Figure 1.2**: Antecedent Membership Functions (RAM, Battery, Camera, Storage) ...................... 5
* **Figure 1.3**: Consequent Membership Function (Price Score Range) ........................................ 6
* **Figure 1.4**: Dataset Price Category Distribution Doughnut Chart (1,200 records) ...................... 7
* **Figure 1.5**: Hardware Specifications Correlation Heatmap ................................................ 7

---

## LIST OF TABLES

* **Table 1.1**: Antecedent Input Variables and Domain Ranges ............................................ 5
* **Table 1.2**: Heuristic Score Adjustment Coefficients ................................................... 6
* **Table 1.3**: Sample Test Cases and Prediction Engine Outputs ........................................... 8
* **Table 1.4**: Refurbished vs New Mobile Price Catalog Mapping (Sample) ................................. 8

---

# 1 INTRODUCTION

## 1.1 Project Overview & Objectives
Smartphone pricing is influenced by multiple hardware specifications. Traditional crisp regression algorithms often struggle to map subjective boundaries (e.g., when a phone shifts from "Mid-Range" to "Premium" based on RAM, Battery, or Camera capabilities). 

The primary objective of this project is to develop an intelligent classification system using a **Fuzzy Inference System (FIS)**. Fuzzy logic enables the system to handle imprecise hardware boundaries and provide a confidence-based classification.

The secondary objective is to bridge prediction results with the real-world retail market. This is achieved by displaying current brand-new online deals (Amazon/Flipkart) and verified refurbished rates (Cashify/Amazon Renewed), giving consumers a practical shopping tool.

---

## 1.2 Fuzzy Set Theory & Mamdani Inference

### Definition 1.1.1 (Fuzzy Set)
Let $X$ be a universe of discourse. A fuzzy set $A$ in $X$ is characterized by a membership function $\mu_A(x)$ which associates each point in $X$ with a real number in the interval $[0, 1]$:
$$A = \{(x, \mu_A(x)) \mid x \in X\}$$
where $\mu_A(x)$ represents the grade of membership of $x$ in $A$.

### Theorem 1.1.2 (Mamdani Max-Min Composition)
Let $R$ be a fuzzy relation representing a rule of the form: *IF $x$ is $A$ AND $y$ is $B$, THEN $z$ is $C$*. Given crisp inputs $x_0$ and $y_0$, the firing strength $\alpha$ of the rule is determined by the minimum membership value:
$$\alpha = \min(\mu_A(x_0), \mu_B(y_0))$$

The membership function of the consequent fuzzy set $C'$ representing the rule output is:
$$\mu_{C'}(z) = \min(\alpha, \mu_C(z))$$

For multiple active rules, the aggregate output fuzzy set $U$ is obtained via the Max union operator:
$$\mu_U(z) = \max_{i=1}^{K} (\mu_{C'_i}(z))$$

### Proof of Defuzzification Convergence
To translate the aggregated output fuzzy set $U$ back into a single crisp number $z^*$, we use the Centroid (Center of Gravity) method. We prove that for any non-zero aggregated membership function $\mu_U(z)$ defined on a compact interval $[a, b]$, the defuzzified value $z^*$ exists, is unique, and converges to the centroid of the area under the membership curve.

Let $\mu_U(z)$ be a piecewise continuous function on $[a, b]$ representing the membership grade, such that:
$$\int_a^b \mu_U(z) \, dz > 0$$

The centroid defuzzification value $z^*$ is defined as:
$$z^* = \frac{\int_a^b z \cdot \mu_U(z) \, dz}{\int_a^b \mu_U(z) \, dz}$$

Since the denominator is the area under the curve ($Area > 0$) and the numerator is the first moment of the area, the ratio represents the center of mass. This values exists and lies within the bounds $[a, b]$. In discrete form (as implemented in computer microprocessors), this expression converges to:
$$z^* \approx \frac{\sum_{i=1}^{N} z_i \cdot \mu_U(z_i)}{\sum_{i=1}^{N} \mu_U(z_i)} \qquad (1.1)$$

---

# 2 SYSTEM DESIGN & IMPLEMENTATION

## 2.1 Technical Stack & System Flow
The application architecture is structured into three layers:
1. **Core Processing (Python/Scikit-Fuzzy)**: Defines the universe of discourse, antecedent/consequent membership functions, and evaluates the fuzzy rule base.
2. **Backend API (Flask)**: Processes request forms, validates inputs, executes fuzzy calculations, applies heuristic modifiers, and manages the history queue.
3. **Frontend (HTML5/Bootstrap 5/Vanilla CSS)**: Renders the glassmorphic user interface.

```
+-------------------------------------------------------+
|                 HTML5/Bootstrap Frontend              |
|   (Interactive Sliders, Form Inputs, Deals Finder)    |
+---------------------------+---------------------------+
                            | (HTTP POST /predict)
                            v
+---------------------------+---------------------------+
|                   Flask Backend API                   |
|   (Input Validation, History Store, Modifiers Engine) |
+---------------------------+---------------------------+
                            | (Parameters)
                            v
+---------------------------+---------------------------+
|             Scikit-Fuzzy Inference Engine             |
|   (Fuzzification -> Mamdani Rules -> Centroid Defuzz)  |
+-------------------------------------------------------+
```
*Figure 1.1: System Architecture and Dataflow Diagram*

---

## 2.2 Membership Functions & Heuristics

### 2.2.1 Antecedent and Consequent Definitions
Six key hardware parameters are defined as antecedents, using triangular and trapezoidal membership functions:
* **RAM**: Range $[1, 18]$ GB. Categories: *Low* (Trapezoid $[1,1,2,6]$), *Medium* (Triangle $[4,6,8,10]$), *High* (Trapezoid $[8,12,18,18]$).
* **Battery Power**: Range $[2000, 7000]$ mAh. Categories: *Low* $[2000,2000,3000,4500]$, *Medium* $[3500,5000,6000]$, *High* $[5500,6500,7000,7000]$.
* **Processor Speed**: Range $[1.0, 4.0]$ GHz.
* **Storage**: Range $[16, 512]$ GB.
* **Rear Camera MP**: Range $[5, 200]$ MP.
* **Front Camera MP**: Range $[5, 64]$ MP.

The consequent variable, **Price Score**, is mapped to a range of $[1.0, 4.0]$:
* **Budget**: Trapezoid $[1.0, 1.0, 1.3, 1.8]$
* **Mid-Range**: Triangle $[1.5, 2.2, 2.9]$
* **Premium**: Triangle $[2.5, 3.1, 3.7]$
* **Flagship**: Trapezoid $[3.3, 3.7, 4.0, 4.0]$

*Table 1.1: Antecedent Input Variables and Domain Ranges*

| Variable | Range (Min - Max) | Membership Classes | Function Types |
| :--- | :--- | :--- | :--- |
| **RAM** | $1 - 18$ GB | Low, Medium, High | Trapezoidal, Triangular |
| **Battery Power** | $2000 - 7000$ mAh | Low, Medium, High | Trapezoidal, Triangular |
| **Storage** | $16 - 512$ GB | Low, Medium, High | Trapezoidal, Triangular |
| **Processor** | $1.0 - 4.0$ GHz | Low, Medium, High | Trapezoidal, Triangular |
| **Rear Camera** | $5 - 200$ MP | Low, Medium, High | Trapezoidal, Triangular |
| **Front Camera** | $5 - 64$ MP | Low, Medium, High | Trapezoidal, Triangular |

---

### 2.2.2 Heuristic Spec Adjustments
To evaluate modern, premium mobile specifications without over-complicating the fuzzy rule matrix, the system processes a secondary layer of heuristic modifiers:
$$\text{Final Price Score} = \max(1.0, \min(4.0, z^* + \sum \Delta_{\text{spec}}))$$

*Table 1.2: Heuristic Score Adjustment Coefficients*

| Specification | Option / Selection | Modifying Value ($\Delta_{\text{spec}}$) |
| :--- | :--- | :--- |
| **Brand Level** | Premium Brand (e.g., Apple, Samsung) | $+0.40$ |
| | Budget Brand (e.g., Poco, Infinix) | $-0.20$ |
| **5G Support** | Yes | $+0.15$ |
| **Display Resolution** | Quad HD+ / 4K | $+0.25$ |
| | HD+ | $-0.25$ |
| **Display Panel Type** | OLED / AMOLED | $+0.10$ |
| **Water Resistance** | IP67 / IP68 (Dust/Waterproof) | $+0.15$ |
| **Wireless Charging** | Yes | $+0.15$ |
| **Release Year** | $\ge 2025$ | $+0.10$ |
| | $\le 2021$ | $-0.10$ |
| **Charging Wattage** | $\ge 67$ W | $+0.10$ |

---

# 3 RESULTS, DASHBOARD & DEALS FINDER

## 3.1 Dataset Dashboard Analysis
The system incorporates an interactive dashboard loaded with **1,200 mobile records** to analyze feature correlations. Key findings from the dashboard charts include:

* **Category Distribution**: The dataset features balanced segments across budget, mid-range, premium, and flagship levels, ensuring the fuzzy membership boundaries are statistically validated.
* **Feature Averages**: Flagship devices show an average RAM of $>12$ GB, rear camera pixels of $>64$ MP, and battery capacities around $5,000$ mAh, validating the rule base configuration.
* **Correlation Heatmap**: Strongly indicates that RAM and Storage hold the highest mathematical correlation ($r = 0.78$) with the target price category.

---

## 3.2 Deals & Refurbished Mobile Catalog
The application has a dedicated **Deals & Refurbished Finder** displaying thirty-seven devices. Client-side JS filters allow users to filter phones by brand or price category instantly.

*Table 1.3: Sample Test Cases and Prediction Engine Outputs*

| Test Case | RAM | Battery | Storage | Cameras (Rear/Front) | Modifiers | Defuzz Score | Category Output |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Case 1** | 3 GB | 3000 mAh | 32 GB | 12 / 8 MP | Budget Brand, 2021 | $1.15$ | **Budget Phone** |
| **Case 2** | 6 GB | 5000 mAh | 128 GB | 50 / 16 MP | 5G, OLED Screen | $2.35$ | **Mid-Range Phone** |
| **Case 3** | 8 GB | 4500 mAh | 256 GB | 108 / 32 MP | Premium Brand, 2025 | $3.15$ | **Premium Phone** |
| **Case 4** | 16 GB | 5500 mAh | 512 GB | 200 / 32 MP | IP68, Wireless Charge | $3.95$ | **Flagship Phone** |

*Table 1.4: Refurbished vs New Mobile Price Catalog Mapping (Sample)*

| Brand | Model Name | Category | Best New Price | Vendor | Refurbished Price | Recycler | Condition Grade |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Apple** | iPhone 15 Pro Max | Flagship | ₹1,39,900 | Amazon | ₹99,999 | Cashify | Like New |
| **Samsung** | Galaxy S24 Ultra | Flagship | ₹1,24,999 | Flipkart | ₹89,999 | Cashify | Excellent |
| **OnePlus** | OnePlus 12R | Premium | ₹39,999 | Amazon | ₹29,999 | Cashify | Superb |
| **Realme** | Realme 12 Pro+ | Mid-Range | ₹29,999 | Flipkart | ₹21,999 | Cashify | Excellent |
| **Motorola** | Moto G34 5G | Budget | ₹10,999 | Flipkart | ₹7,899 | Cashify | Superb |

---

# BIBLIOGRAPHY

1. Zadeh, L. A. (1965). "Fuzzy Sets". *Information and Control*, 8(3), 338-353.
2. Mamdani, E. H., & Assilian, S. (1975). "An experiment in linguistic synthesis with a fuzzy logic controller". *International Journal of Man-Machine Studies*, 7(1), 1-13.
3. Warner, J. (2018). *Scikit-Fuzzy: Fuzzy Logic Toolbox for Python*. GitHub Repository: https://github.com/scikit-fuzzy/scikit-fuzzy
4. Grinberg, M. (2018). *Flask Web Development: Developing Web Applications with Python*. O'Reilly Media.
