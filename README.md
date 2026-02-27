# Food Saver – Anti Food Waste App 🌍🍎

**Food Saver** is a Django-based web application designed to reduce food waste by connecting food donors (restaurants, grocery stores, and households) with recipients (NGOs and individuals in need).

## 🚀 Features

### 👤 User Roles
- **Donors:** Easily list surplus food, upload images, and get AI-predicted expiry times.
- **Volunteers:** Find food pickup requests, navigate using interactive maps, and earn reward points for successful deliveries.
- **Admins:** Oversee the platform, manage users, and monitor fraud detection.

### 🛠 Tech Stack
- **Backend:** Django (Python)
- **Frontend:** HTML5, CSS3, JavaScript
- **Maps:** Leaflet.js
- **Deployment Ready:** Includes `Procfile` and `build.sh` for easy deployment to Render.

## 📦 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Gayatri-215/food_saver.git
   cd food_saver
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

## 🌐 Deployment to Render

This project is configured for deployment on [Render](https://render.com/).

1. Connect your GitHub repository to Render.
2. Create a new **Web Service**.
3. Use the following settings:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn food_saver_project.wsgi`
4. Add any necessary environment variables in the Render dashboard.

---
Developed as part of the Gayatri-215 Food Saver project.
