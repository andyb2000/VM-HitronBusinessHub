| Endpoint                 | Method | Auth | CSRF | Source JS    | Status     | Notes               |
| ------------------------ | ------ | ---- | ---- | ------------ | ---------- | ------------------- |
| `/1/Device/Users/Login`  | POST   | No   | No   | `login.html` | ✅ Verified | Takes `model=` JSON |
| `/1/Device/Users/CSRF`   | GET    | Yes  | N/A  | `mainApp.js` | ✅ Verified | Returns JSON token  |
| `/1/Device/CM/Basicinfo` | GET    | No   | No   | `login.html` | ✅ Verified | Used before login   |
