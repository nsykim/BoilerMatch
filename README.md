# BoilerMatch  
Roommate Matching Service

## Overview
BoilerMatch is a mobile app designed to match roommates based on lifestyle preferences. It consists of a TypeScript + Expo frontend and a Python backend. Users can set preferences, view compatible roommates, swipe to match, and chat with others through a mobile interface.

## Project Structure
BoilerMatch/\
─ frontend/\
─ src/\
─ tests/\
─ README.md

## Setup Instructions

### Backend
1. Navigate to the backend directory:
   `cd src`

2. (Optional) Create and activate a virtual environment:
   `python -m venv venv`  
   source venv/bin/activate  # or venv\Scripts\activate on Windows

3. Install dependencies:
   `pip install -r requirements.txt`

4. Start the API:
   `python api.py`

The API will be hosted on your computer's local IPv4 address (e.g., http://192.168.x.x:3020).  
You must use this address instead of localhost so the mobile app can connect from another device on the same network.

---

### Frontend
1. Open a new terminal and navigate to the frontend directory:
   `cd frontend`

2. Install dependencies:
   `npm install`

3. Start the app:
   `npx expo start`

4. Install Expo Go:
   - Download Expo Go from the App Store (iOS) or Google Play (Android).

5. Scan the QR Code:
   - After running `npx expo start`, scan the QR code using Expo Go to open the app on your device.

Make sure your mobile device is connected to the same Wi-Fi network as the computer running the backend.

---

## Running Tests
- All integration and unit tests are located in the `tests/` directory.
- Tests are automatically run on all `integration/*` branches via GitHub Actions CI.

---

## Branch Strategy

- `integration/dev`: Most up-to-date supported branch. Deployed to dev server.
- `[name]/integration/BM[Jira Ticket Number]`: Integration dev branch for a specific feature.
- `[name]/personal/BM[Jira Ticket Number]`: Individual feature branch, WIP, may not pass automated tests.
