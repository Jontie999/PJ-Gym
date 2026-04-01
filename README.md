# Gym Tracker

A mobile-first Progressive Web App (PWA) for tracking gym workouts, monitoring progress, and syncing data across devices via Firebase.

## One App — Works on iPhone and Android

**Yes — a single version of this app works on both iPhone and Android.** There is no separate iOS or Android build. Because it is a **Progressive Web App (PWA)**, it runs in the browser on any device and can be added to your home screen for a native app-like experience, with no app store required.

| Platform | Support | How to Install |
|----------|---------|----------------|
| 🤖 **Android** | ✅ Full support | Open in Chrome → tap **⋮ Menu → Add to Home screen** |
| 🍎 **iPhone / iOS** | ✅ Full support | Open in Safari → tap **Share → Add to Home Screen** |
| 🖥️ **Desktop** | ✅ Full support | Open in any modern browser |

---

## Features

- 💪 Log workouts with exercises, sets, reps, and weight
- 📊 View progress charts and analytics (frequency, volume, PRs)
- ☁️ Real-time sync across devices with Firebase
- 🔐 Secure login with email and password
- ⏱️ Built-in rest timer between sets
- 📴 Offline support with local storage fallback

---

## Installation Guide

### 🤖 Android

1. Open **Google Chrome** on your Android device
2. Navigate to the Gym Tracker URL
3. Tap the **⋮ menu** (three dots) in the top-right corner
4. Select **"Add to Home screen"**
5. Tap **"Add"** to confirm

### 🍎 iPhone / iOS

1. Open **Safari** on your iPhone (must be Safari — Chrome on iOS does not support PWA installation)
2. Navigate to the Gym Tracker URL
3. Tap the **Share button** (the box with an arrow pointing up) at the bottom of the screen
4. Scroll down and tap **"Add to Home Screen"**
5. Tap **"Add"** to confirm

Once installed on either platform, the app launches in full-screen mode just like a native app and continues to work offline.

---

## Running Locally

No build step is required — it's a single HTML file.

```bash
# Using Python
python3 -m http.server 8000
# Then open http://localhost:8000 in your browser
```

---

## Tech Stack

- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Backend**: Firebase (Firestore + Authentication)
- **Charting**: Custom canvas-based charts
