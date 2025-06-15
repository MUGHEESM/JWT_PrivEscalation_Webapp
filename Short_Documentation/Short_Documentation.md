# Short Documentationn

### 2. Short Documentation about Architecture & Tech Stack, and Location/Rationale of the Flaw 

**Architecture & Tech Stack:**

- **Client-Server Architecture:** The application follows a traditional client-server model. The frontend (HTML/CSS/JS) sends requests to the Flask backend.
- **Flask Framework:** A lightweight Python web framework used for handling HTTP requests, routing, and rendering templates.
- **JSON Web Tokens (JWT):** Used for session management. When a user logs in, the server issues a signed JWT. This token is then stored in the client's browser as an `httponly` cookie and sent with subsequent requests to authenticate and authorize the user.
- **PyJWT Library:** A Python library for encoding and decoding JWTs.
- **Hardcoded Users:** For simplicity, user credentials and roles are stored directly in the `app.py` file. In a real application, a database would be used.
- **Cookie-based Token Storage:** The JWT is stored in an `httponly` cookie to mitigate XSS attacks (though storing JWTs in cookies can have other considerations regarding CSRF if not handled correctly, which is beyond the scope of this minimal example).

**Session Management with JWT:**

1. **Login:** User provides username and password to `/login`.
2. **Authentication:** Server verifies credentials against hardcoded users.
3. **JWT Issuance:** If credentials are valid, a JWT is created containing the `username` and `role` in its payload, along with an expiration timestamp. The token is signed with a `SECRET_KEY`.
4. **Token Storage:** The signed JWT is sent back to the client and stored as an `httponly` cookie named `jwt_token`.
5. **Protected Endpoints:** For subsequent requests to protected endpoints (e.g., `/dashboard`, `/admin/dashboard`), the client automatically sends the `jwt_token` cookie.
6. **Authorization:** The `jwt_required` and `admin_required` decorators on the server side extract the token, decode it using the `SECRET_KEY`, and then use the `role` from the payload to determine if the user is authorized to access the requested resource.

**Location and Rationale of the Flaw (Privilege Escalation):**

- **Location:** The deliberate access-control flaw is located within the `admin_required` decorator in `app.py`, specifically in the line:
    
    `if 'admin' not in data.get('role', ''):`
    
- **Rationale:**
    - **Intention (Vulnerable Code):** The intention was to check if the user's `role` is exactly 'admin'. However, the implementation uses the `in` operator, which checks for substring presence.
    - **Exploitation:** If a normal user (`user`) has their JWT payload modified (e.g., via a proxy tool like Burp Suite or by forging a token if the secret key is leaked) to have a `role` claim like `"user;admin"` or `"superadmin"`, the `if 'admin' not in data.get('role', '')` condition will evaluate to `False` (because 'admin' *is* in "user;admin"), thus granting them access to the `/admin/dashboard` endpoint.
    - **Correct (Secure) Implementation:** The correct and secure way to check for an exact role match would be:
    This exact comparison would prevent any substring-based circumvention.
        
        `if data.get('role') != 'admin':`
