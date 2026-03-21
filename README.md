# 🚌 SmartTransit

SmartTransit is a modern, AI-powered public transportation management system designed to enhance commuter safety and provide real-time bus tracking. The project integrates traditional transit management with advanced security features like AI-based facial recognition to identify criminals and missing persons in real-time.

---

## 🚀 Key Features

-   **Real-time Tracking**: Commuters can track buses and view nearby transit options.
-   **AI Safety Alerts**: Bus cameras automatically detect registered criminals or missing persons.
-   **Multi-Role Dashboards**: Tailored experiences for Admins, Drivers, Police, and Passengers.
-   **Complaint Management**: Secure platform for users to report issues directly to police stations.
-   **Security Databases**: centralized management of criminal and missing person records.

---

## 🛠️ Tech Stack

### Backend
-   **Framework**: Flask (Python)
-   **Database**: PostgreSQL with SQLAlchemy ORM
-   **Authentication**: JWT (JSON Web Tokens) & Bcrypt
-   **Real-time**: Flask-SocketIO
-   **AI Engine**: Python `face_recognition` and `OpenCV`

### Frontend
-   **UI**: Vanilla HTML5, CSS3, & Bootstrap 5
-   **Logic**: Modern JavaScript (Vanilla)
-   **API Handling**: Shared `api.js` helper for JWT-secured fetches

---

## 📂 Project Structure

```text
Smart_Transit/
├── backend/                # Flask API Server
│   ├── ai/                 # Facial detection logic
│   ├── models/             # SQLAlchemy Database Models
│   ├── routes/             # Role-specific API endpoints (Admin, User, Driver, etc.)
│   ├── uploads/            # Storage for detection images and profile photos
│   └── app.py              # Application Entry Point
├── web/                    # Frontend Files
│   ├── admin/              # Administrator Dashboard
│   ├── assets/             # CSS, Shared JS, and Images
│   ├── driver/             # Bus Driver Portal
│   ├── police/             # Law Enforcement Interface
│   └── user/               # Passenger/User App
└── database/               # Database schemas and seed scripts
```

---

## 👥 User Roles & Permissions

| Role | Permissions & Capabilities |
| :--- | :--- |
| **Admin** | Manage Routes/Buses, Approve Drivers, Add Police Stations, View System Analytics. |
| **User** | Track Nearby Buses, Search Routes, File Complaints, Post Reviews, View Safety Alerts. |
| **Driver** | View Assigned Route, Update Live Location, Receive Safety Alerts, View Bus Reviews. |
| **Police** | Manage Criminal/Missing DBs, Resolve AI Alerts, View & Action Complaints. |

---

## 🔄 Core Workflows

### 1. Real-time Tracking Flow
1.  **Driver** logs in and starts their route via the "Update Location" page.
2.  The **System** updates the bus's GPS coordinates in the PostgreSQL database.
3.  **User** opens the "Find Bus" page and sees the live location of all active buses on their dashboard.

### 2. AI Safety Alert Flow
1.  **On-board Camera** sends a frame to the `/api/camera/detect` endpoint.
2.  The **AI Engine** scans the frame against the Criminal or Missing Person database.
3.  If a **Match** is found:
    -   A `CameraDetection` record is created in the database.
    -   An **Alert** is instantly broadcasted to the **Driver's** dashboard.
    -   The **Police** receive a high-level notification to take action.
    -   **Users** can see safety alerts in their public feed.

---

## ⚙️ Setup & Installation

### Prerequisites
-   Python 3.10+
-   PostgreSQL Database
-   Web Browser (Chrome/Edge/Firefox)

### Installation Steps
1.  **Clone the Repository**.
2.  **Setup Backend**:
    ```powershell
    cd backend
    pip install -r requirements.txt
    ```
3.  **Environment Configuration**: Create a `.env` file in the `backend/` folder:
    ```env
    DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/smarttransit_db
    JWT_SECRET_KEY=your_secret_key
    ```
4.  **Run Application**:
    ```powershell
    python app.py
    ```
5.  **Access Web**: Open `http://127.0.0.1:5000` in your browser.

---

## 🔍 Testing & Bug Verification Checklist

To ensure the entire app is working correctly, follow these steps:

- [ ] **Admin Setup**: Login with `admin@smarttransit.com` / `admin123`. Create a sample route and assign a bus to a driver.
- [ ] **Auth Check**: Ensure that a "User" cannot access `/web/admin/` or `/web/driver/` pages (Role-based access control).
- [ ] **Driver Tracking**: Log in as a Driver, update your location, and verify that the "Last Updated" timestamp changes.
- [ ] **User Search**: Log in as a User and confirm that the bus created by the Admin appears in "Search Nearby".
- [ ] **AI Detection**: Use the AI Camera test tool to upload an image of a "Registered Criminal". 
    - [ ] Verify an alert appears in the **Police Dashboard**.
    - [ ] Verify the **Driver Dashboard** shows a red indicator.
- [ ] **Complaints**: File a complaint as a User and verify it appears in the specific **Police Station's** dashboard for investigation.
