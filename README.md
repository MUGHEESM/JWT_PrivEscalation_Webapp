# JWT_PrivEscalation_Webapp
Minimal web app using JWT (RFC 7519) with a deliberate access-control flaw allowing privilege escalation via token manipulation.

## Table of Contents

- Features
- Tech Stack
- Setup Instructions
- Execution Commands
- User Accounts
- Deliberate Flaw (Privilege Escalation)
- Security Notes

## Features

- User login with JWT-based session management.
- Two roles: `user` and `admin`.
- Protected endpoints (`/user/dashboard`, `/admin/dashboard`).
- A deliberate flaw in access control to allow privilege escalation for regular users.

## Tech Stack

- **Backend:** Python 3, Flask, PyJWT
- **Frontend:** HTML, Basic CSS

## Setup Instructions

1. **Clone the Repository (or create files manually):**
If you have the files in a repository, clone it:
    
    `git clone <repository_url>
    cd jwt-privilege-escalation-app`
    
    Otherwise, create the file structure and files as described in the "Source Code" section above.
    
2. **Create a Python Virtual Environment (Recommended):**
    
    `python3 -m venv venv`
    
3. **Activate the Virtual Environment:**
    - **On Linux/macOS:**
        
        `source venv/bin/activate`
        
    - **On Windows:**
        
        `.\venv\Scripts\activate`
        
4. **Install Dependencies:**
    
    `pip install Flask PyJWT`
    

## Execution Commands

1. **Set the Flask Secret Key (Optional but good practice):**
The `app.config['SECRET_KEY']` is used for signing JWTs. For production, it's crucial to use a strong, unique, and environment-variable-based key.
    
    `export FLASK_SECRET_KEY='your_very_strong_and_secret_key_here'
    # For Windows: set FLASK_SECRET_KEY=your_very_strong_and_secret_key_here`
    
    If you don't set this, a default hardcoded key will be used (`super-secret-key-for-jwt-signing`), which is acceptable for this demonstration but highly insecure for real-world applications.
    
2. **Run the Flask Application:**
    
    `python app.py`
    
    The application will typically run on `http://127.0.0.1:5000/`.
    

## User Accounts

The following hardcoded user accounts are available:

- **Normal User:**
    - **Username:** `user`
    - **Password:** `password123`
    - **Role:** `user`
- **Admin User:**
    - **Username:** `admin`
    - **Password:** `adminpassword`
    - **Role:** `admin`

## Deliberate Flaw (Privilege Escalation)

This application contains a deliberate access-control flaw to demonstrate privilege escalation.

**The Flaw:**
In `app.py`, the `admin_required` decorator checks for the presence of the substring 'admin' within the user's `role` claim in the JWT payload, rather than checking for an exact match.

**Exploitation Steps (Example):**

1. **Log in as a normal user:** Go to `http://127.0.0.1:5000/` and log in with `username: user`, `password: password123`.
2. **Observe the JWT:** After successful login, inspect your browser's cookies. You will find an `httponly` cookie named `jwt_token`.
3. **Copy the JWT:** Copy the value of this `jwt_token` cookie.
4. **Decode the JWT (Optional but Recommended):** Use an online JWT decoder (e.g., `jwt.io`) to see the payload. You'll see something like `{"username": "user", "role": "user", "exp": ...}`.
5. **Forge a New JWT:**
    - **If you know the `SECRET_KEY` (which is `super-secret-key-for-jwt-signing` if not overridden):** You can use `jwt.io` or a Python script to create a *new* JWT with a modified `role`. Change the payload to `{"username": "user", "role": "user;admin", "exp": ...}`.
    - **Without knowing the `SECRET_KEY` (more realistic scenario for black-box testing):**
    This is more complex. You would typically need to exploit another vulnerability (like an SQL injection or a file inclusion) to retrieve the secret key, or attempt a brute-force attack on a weak secret key (which is why `super-secret-key-for-jwt-signing` is a bad idea). *For the purpose of this demonstration, we are assuming you have access to or can guess the secret key to forge a token, or are using a tool that allows token modification in transit (e.g., Burp Suite).*
6. **Modify the Cookie:**
    - **Using Browser Developer Tools:** In your browser's developer tools (F12), go to "Application" -> "Cookies". Find the `jwt_token` cookie for `http://127.0.0.1:5000`.
    - **Paste the new, forged JWT** into the `Value` field of the `jwt_token` cookie.
    - **Using a Proxy Tool (e.g., Burp Suite):** Intercept the request to `/user/dashboard` (or any protected endpoint). Modify the `jwt_token` cookie in the intercepted request to include your forged token with `{"role": "user;admin"}`.
7. **Access the Admin Dashboard:** Now, try to navigate to `http://127.0.0.1:5000/admin/dashboard`. You should now be able to access it as a "normal" user.

## Security Notes

- **DO NOT USE THE This `SECRET_KEY` IN PRODUCTION!** The `super-secret-key-for-jwt-signing` is extremely insecure. Always use a strong, randomly generated, and securely managed secret key for production applications.
- **HTTPS is Crucial:** For production environments, always serve your application over HTTPS to protect JWTs from eavesdropping. The current `secure=False` for cookies in `app.py` is for local development convenience.
- **CSRF Protection:** While `httponly` cookies mitigate XSS for JWTs, they are still vulnerable to CSRF if not properly protected. This minimal app does not include CSRF tokens.
- **Token Revocation:** This example does not implement JWT revocation. Once a token is issued, it remains valid until its expiration. In a real application, you might need a mechanism (e.g., a blacklist) to invalidate tokens before their natural expiration.
- **Rate Limiting:** Login endpoints should always have rate limiting to prevent brute-force attacks.
