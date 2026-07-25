<div align="center">

# 🧴 Product Sense

### AI-powered beauty product scanner that reads the label so you don't have to.

<p>
Scan any beauty product, understand what's inside it, and receive personalized ingredient insights based on your skin type.
</p>

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)]()

[Demo](#-demo) • [Features](#-features) • [Tech Stack](#-tech-stack) • [Quick Start](#-quick-start) • [How It Works](#-how-it-works)

</div>

---

## 💡 Inspiration

Standing in a drugstore aisle trying to figure out whether a product is actually safe for your skin—or hiding questionable ingredients behind marketing buzzwords—is harder than it should be. Nobody asked me to fix this; I just got tired of squinting at tiny labels under bad lighting and decided to build something smarter.

**Product Sense** scans beauty products, identifies them, breaks down their ingredients into plain language, and helps you decide whether they're a good fit for your skin.

---

## 🎥 Demo

> _Add a screenshot or GIF here showcasing the product recognition and ingredient analysis workflow._

---

## ✨ Features

- 📸 **Snap and identify** — scan any beauty product with your camera and get instant recognition.
- 🧪 **Ingredient breakdown** — decodes complex INCI ingredient lists into plain language.
- 🎯 **Skin type matching** — evaluates whether a product suits your skin type.
- ⚠️ **Ingredient alerts** — highlights ingredients that may cause irritation or concern.
- 🔍 **Retrieval-based product matching** — compares products against a curated database instead of relying solely on rigid label matching.

---

## 🛠 Tech Stack

| Layer | Technology |
| ------ | ---------- |
| Backend | Python, FastAPI |
| Vision | Custom product recognition pipeline (`vision.py`) |
| Intelligence | Retrieval-based reasoning engine (`intelligence.py`) |
| Data | Product & ingredient dataset (`products.xlsx`) |
| Frontend | HTML, CSS, JavaScript |

---

## ⚙️ How It Works

Product Sense combines a vision model for product recognition with a retrieval layer that cross-references ingredient and skin-type data instead of relying purely on OCR or exact label matching.

Beauty products are visually similar—near-identical bottle shapes, packaging, and fonts often confuse traditional image classification models. To improve reliability, Product Sense retrieves visually and semantically similar products from its database before analyzing ingredients and generating personalized recommendations.

### Pipeline

```text
Image
   │
   ▼
Product Recognition
   │
   ▼
Retrieve Matching Product
   │
   ▼
Ingredient Analysis
   │
   ▼
Skin Compatibility Check
   │
   ▼
Personalized Recommendation
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
git clone https://github.com/Rijul-chadha/Product-Sense.git
cd Product-Sense
pip install -r requirements.txt
```

### Run Locally

```bash
python run.py
```

Then open the frontend in your browser to start scanning.

---

## 📂 Project Structure



```text
Product-Sense/
├── backend/
│   ├── dataset.py
│   ├── intelligence.py
│   ├── main.py
│   ├── models.py
│   └── vision.py
├── data/
│   └── products.xlsx
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
├── requirements.txt
├── run.py
└── README.md
```

---

## 🧗 Challenges I Ran Into

- Public product image datasets are scarce and inconsistent, making reliable recognition challenging.
- Near-identical packaging across brands often fooled straightforward classification approaches.
- Reliably identifying potentially concerning ingredients required parsing messy and inconsistent ingredient lists instead of simply matching keywords.

---

## 🔭 What's Next

- Expand the ingredient and product database for broader brand coverage.
- Add barcode scanning as a faster alternative to image recognition.
- Build more granular skin sensitivity profiles for personalized recommendations.
- Improve recognition accuracy with a larger product image dataset.

---

## 👤 Author

Built by **[Rijul Chadha](https://github.com/Rijul-chadha)** — Computer Science student at Toronto Metropolitan University, focused on AI/ML and full-stack development.

---

<div align="center">

⭐ If you found this project interesting, consider giving it a star!

</div>
