## Advanced Library Management System
Build a library management system to manage libraries, books, authors, and categories. Implement user registration, login, and password recovery. Allow users to borrow and return multiple books in one transaction, with notifications and real-time updates for book availability.

---

## 🚀 Running the Project with Docker

### 1. **Clone the Repository**
```sh
git clone <your-repo-url>
cd library_project
```

### 2. **Build and Start the Containers**
```sh
docker-compose up --build
```
This will start the following services:
- **web**: Django app (ASGI, Uvicorn)
- **db**: PostgreSQL database
- **redis**: Redis for caching, Celery, and sessions
- **celery**: Celery worker for background tasks
- **celery-beat**: Celery Beat for scheduled tasks


### 4. **Create a Superuser (Optional)**
```sh
docker-compose exec web python manage.py createsuperuser
```

### 5. **Access the Application**
- Django app: [http://localhost:8000](http://localhost:8000)
- Django admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## ✉️ Email Sending (Mailtrap)

This project uses [Mailtrap](https://mailtrap.io/) for email testing in development.

### **How to Configure Mailtrap:**
1. Go to [mailtrap.io](https://mailtrap.io/) and sign up/log in.
2. Create an inbox and go to its SMTP settings.
3. Copy the following variables from Mailtrap and update them in your `docker-compose.yml` under the `web`, `celery`, and `celery-beat` services:

```
EMAIL_HOST=<your-mailtrap-host>
EMAIL_HOST_USER=<your-mailtrap-username>
EMAIL_HOST_PASSWORD=<your-mailtrap-password>
EMAIL_PORT=<your-mailtrap-port>
```

**Example:**
```
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_HOST_USER=your_mailtrap_user
EMAIL_HOST_PASSWORD=your_mailtrap_password
EMAIL_PORT=2525
```

---

## 📚 API Endpoints

### **Authentication & User Management**

#### **Register**
- **POST** `/api/auth/registration/`
- **Body:**
  ```json
  {
    "username": "string",
    "email": "string",
    "password1": "string",
    "password2": "string"
  }
  ```

#### **Login**
- **POST** `/api/auth/login/`
- **Body:**
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```

#### **Logout**
- **POST** `/api/auth/logout/`

#### **Password Reset (Request)**
- **POST** `/api/auth/password/reset/`
- **Body:**
  ```json
  {
    "email": "string"
  }
  ```

#### **Password Reset (Confirm)**
- **POST** `/api/auth/password/reset/confirm/<uidb64>/<token>/`
- **Body:**
  ```json
  {
    "new_password1": "string",
    "new_password2": "string"
  }
  ```

#### **Profile**
- **GET** `/api/accounts/profile/`
- **PATCH** `/api/accounts/profile/`
- **Body (PATCH):**
  ```json
  {
    "username": "string",
    "email": "string",
    "latitude": 40.712776,
    "longitude": -74.005974
  }
  ```

---

### **Library, Author, and Book Endpoints**

#### **List Libraries**
- **GET** `/api/libraries/`
- **Query Params:**  
  - `category` (optional): filter by category name  
  - `author` (optional): filter by author name

#### **List Authors**
- **GET** `/api/authors/`
- **Query Params:**  
  - `category` (optional): filter by book category name  
  - `library` (optional): filter by library ID

#### **List Books**
- **GET** `/api/books/`
- **Query Params:**  
  - `category` (optional): filter by category ID  
  - `author` (optional): filter by author ID  
  - `library` (optional): filter by library ID

#### **List Author Details**
- **GET** `/api/authors-details/`
- **Query Params:**  
  - `category` (optional): filter by category ID  
  - `library` (optional): filter by library ID

---

### **Borrowing Books**

#### **Borrow Books**
- **POST** `/api/books/borrow/`
- **Body:**
  ```json
  {
    "book_ids": [1, 2, 3],      // up to 3 book IDs
    "due_date": "YYYY-MM-DD",   // max 1 month from now
    "library_id": 1
  }
  ```

#### **Return Books**
- **POST** `/api/books/borrow/return/`
- **Body:**
  ```json
  {
    "book_ids": [1, 2]
  }
  ```

---

### **Other Endpoints**

- **Django Admin:** `/admin/`

---
