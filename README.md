# Gym Tracker

A mobile-first Progressive Web App (PWA) for tracking gym workouts, monitoring progress, and syncing data across devices via Firebase.

## Features

- 💪 Log workouts with exercises, sets, reps, and weight
- 📊 View progress charts and analytics (frequency, volume, PRs)
- ☁️ Real-time sync across devices with Firebase
- 🔐 Secure login with email and password
- ⏱️ Built-in rest timer between sets
- 📴 Offline support with local storage fallback

## Platform Support

Gym Tracker is a **Progressive Web App (PWA)** and runs in any modern browser — no app store required.

| Platform | Support | How to Use |
|----------|---------|------------|
| 🤖 **Android** | ✅ Full support | Open in Chrome → tap **⋮ Menu → Add to Home screen** |
| 🍎 **iOS** | ✅ Full support | Open in Safari → tap **Share → Add to Home Screen** |
| 🖥️ **Desktop** | ✅ Full support | Open in any modern browser |

## Android Installation

To install Gym Tracker on your Android device for an app-like experience:

1. Open **Google Chrome** (or any Chromium-based browser) on your Android device
2. Navigate to the Gym Tracker URL
3. Tap the **⋮ menu** (three dots) in the top-right corner
4. Select **"Add to Home screen"**
5. Tap **"Add"** to confirm

The app will appear on your home screen and launch in full-screen mode, just like a native app. It also works offline once loaded.

## Running Locally

No build step is required — it's a single HTML file.

```bash
# Using Python
python3 -m http.server 8000
# Then open http://localhost:8000 in your browser
```

## Tech Stack

- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Backend**: Firebase (Firestore + Authentication)
- **Charting**: Custom canvas-based charts
