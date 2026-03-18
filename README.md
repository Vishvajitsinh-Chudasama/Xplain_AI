## Xplain_AI

Xplain_AI is a Django-based web application that showcases **Explainable AI (XAI)** using **SHAP (SHapley Additive exPlanations)**. The project is built around the idea that ML models should not behave like black boxes—each prediction should be interpretable, auditable, and easier to trust.

The codebase currently includes:

- **Explainability-focused dashboard/landing page** (SHAP concepts, formulas, and rationale)
- **Authentication module** with **OTP-based signup** (email OTP) and a login UI

---

### Why SHAP? (Explainability Features)

SHAP is used to explain *individual predictions* from a machine learning model by attributing the prediction to its input features.

- **Feature attribution per prediction (local explanations)**: for a single input, SHAP assigns a contribution value \(\phi_i\) to each feature \(i\), indicating how much that feature pushed the prediction up or down relative to a baseline.
- **Additive explanation model**: SHAP explanations can be written as an additive model:

  ```text
  g(z') = φ₀ + Σᵢ φᵢ zᵢ'
  ```

  Where:

  - `g` is the explanation model
  - `z' ∈ {0,1}^M` is the simplified input (feature present/absent)
  - `φ₀` is the base value (expected model output / baseline)
  - `φᵢ` is the SHAP value (contribution) for feature `i`

- **Game-theoretic fairness (Shapley values)**: SHAP values come from Shapley values, which compute a feature’s average marginal contribution across all possible feature coalitions:

  ```text
  φᵢ = Σ_{S ⊆ N \ {i}}  ( |S|! (|N| − |S| − 1)! / |N|! ) · [ fₓ(S ∪ {i}) − fₓ(S) ]
  ```

- **Model-agnostic**: SHAP can be applied to many model families (trees, linear models, neural nets) without changing the explanation principle.
- **Local accuracy**: the sum of SHAP values plus the base value matches the model’s prediction for that instance.
- **Local + global insight**: per-instance explanations (why this prediction?) and aggregated importance (what generally matters most?).

In this repository, SHAP is currently presented as a **well-structured educational dashboard** (text, equations, and static visuals) that can later be connected to real model outputs and SHAP plots (force plots, beeswarm/summary plots, dependence plots).

---

### Project Structure

- `Xplain_AI/`
  - `settings.py` – Django project settings (apps, middleware, DB, templates, static URL).
  - `urls.py` – Root routes.
- `dashboard/`
  - `views.py` – `dashboard` view.
  - `urls.py` – Maps `/` to the dashboard page.
  - `templates/dashboard.html` – Explainability/SHAP landing content (Tailwind via CDN).
- `check_auth/`
  - `models.py` – `UserInfo` and `OTP` models.
  - `views.py` – Login page render + OTP-based signup flow (send/verify via JSON POST).
  - `urls.py` – Maps `/auth/login/` and `/auth/signup/`.
  - `templates/`
    - `login.html` – Login UI (no backend auth implemented yet).
    - `signup.html` – Signup UI + JS for send/verify OTP calls.
    - `otp.html` – HTML email template used to send OTP.
- `manage.py` – Django entrypoint.

---

### Routes

Defined in `Xplain_AI/urls.py`:

- **Dashboard**: `GET /` → renders `dashboard.html`
- **Auth**:
  - `GET /auth/login/` → renders `login.html`
  - `GET /auth/signup/` → renders `signup.html`
  - `POST /auth/signup/` → JSON API for OTP send/verify (see below)
- **Admin**: `GET /admin/`

---

### OTP Signup Flow (Current Implementation)

`check_auth.views.signup_view` supports two JSON actions:

1. **Send OTP**

`POST /auth/signup/`

```json
{
  "action": "send",
  "name": "Your Name",
  "email": "you@example.com"
}
```

Backend behavior:

- Checks if `UserInfo` already exists for that email
- Generates a 6-digit OTP
- Saves it in `OTP` (update-or-create by email)
- Loads `check_auth/templates/otp.html` and replaces `{{ username }}` and `{{ otp }}`
- Sends the OTP via SMTP

2. **Verify OTP + Create Account**

`POST /auth/signup/`

```json
{
  "action": "verify",
  "name": "Your Name",
  "email": "you@example.com",
  "phone": "1234567890",
  "password": "your-password",
  "otp": "123456"
}
```

Backend behavior:

- Fetches OTP record by email
- Validates:
  - OTP matches
  - OTP age within **5 minutes** (`OTP.is_valid()`)
- Creates `UserInfo`
- Deletes OTP record after successful signup

---

### Tech Stack

- **Backend**: Django (project generated using Django 5.2.x)
- **Database**: SQLite (`db.sqlite3`)
- **Frontend**:
  - Tailwind CSS via CDN (`dashboard.html`)
  - Inline CSS (`login.html`, `signup.html`)
- **Email**: SMTP (configured for Gmail in code)

---

### Setup (Local Development)

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install "Django>=5.2,<6.0"
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Start the server:

```bash
python manage.py runserver
```

Open:

- `http://127.0.0.1:8000/` – SHAP explainability dashboard
- `http://127.0.0.1:8000/auth/signup/` – OTP signup
- `http://127.0.0.1:8000/auth/login/` – login UI

---

### Configuration Notes (Important)

- **SMTP credentials** are currently hard-coded in `check_auth/views.py`:
  - `SENDER_EMAIL = "sender@gmail.com"`
  - `SENDER_PASSWORD = "password"`

For real usage, move these values to environment variables and load them securely.

---

### Security Notes / Limitations

This codebase is currently best treated as a **demo/learning project**:

- **Passwords are stored in plain text** in `UserInfo.password` (not safe).
- Signup endpoint is `@csrf_exempt` (not ideal).
- `DEBUG=True` and `ALLOWED_HOSTS=[]` in `settings.py`.

Recommended next steps if you’re turning this into a real platform:

- Use Django’s built-in authentication (`django.contrib.auth`) with hashed passwords.
- Remove `@csrf_exempt` and handle CSRF properly for JSON requests.
- Add rate-limiting for OTP sends and verification attempts.
- Store secrets in environment variables.
- Integrate real ML models and compute SHAP values dynamically, then render SHAP plots on the dashboard.
