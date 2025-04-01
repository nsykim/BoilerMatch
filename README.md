# Boiler Match
Roommate Matching Service

- Aidan Poor 
- Mitchel Craven 
- Noah Kim

## Branch Strategy:
- integration/dev - most up-to-date supported branch. Deployed onto dev server
- [name]/integration/BM[Jira Ticket Number] - integration development branch for specified feature
- [name]/personal/BM[Jira Ticket Number] - feature development branch for specified feature (DOES NOT PASS AUTOMATED TESTS)

## 🛠️ Local Development & Packaging Process

BoilerMatch uses a two-part architecture:
- **Backend:** Python FastAPI
- **Frontend:** React Native (via Expo)

### 🔧 Configuration
Before starting, update the `API_BASE_URL` in `frontend/boilermatch/constants/config.ts` to match your local IPv4 address:

```ts
export const API_BASE_URL = "http://192.168.1.46:3020"; //CHANGE THIS EACH TIME YOU MOVE
