from fastapi import FastAPI
from app.routes import router
from app.models import User
from app.repository import user_repository

app = FastAPI(
    title="Habit Gamification API",
    description="""
## Habit Gamification API

API untuk mengelola habit tracking dengan fitur gamifikasi.

### Features

* **Authentication** - Login dengan JWT token
* **Create Habits** - Buat habit baru dengan judul dan deskripsi
* **Track Progress** - Lacak progres penyelesaian habit
* **Streak Tracking** - Hitung streak berturut-turut
* **Complete/Miss** - Tandai habit sebagai selesai atau terlewat

### Authentication

Semua endpoint habit memerlukan autentikasi menggunakan JWT token.
Gunakan endpoint `/api/auth/login` untuk mendapatkan token, kemudian sertakan di header:

```
Authorization: Bearer <your-jwt-token>
```

### Domain Model

- **User**: Entity untuk autentikasi pengguna
- **Habit**: Aggregate root yang menyimpan informasi habit
- **Progress**: Value object untuk tracking completed/total entries
- **Streak**: Value object untuk menghitung streak berturut-turut
- **HabitEntry**: Entity untuk mencatat penyelesaian harian
    """,
    version="1.0.0",
    contact={
        "name": "Habit Gamification Team",
    },
    license_info={
        "name": "MIT",
    },
)


@app.on_event("startup")
def startup_event():
    """Create test users on startup"""
    # Create a test user for development (only if doesn't exist)
    existing_user = user_repository.get_by_username("test_user")
    if not existing_user:
        test_user = User.create(username="test_user", password="test_password")
        user_repository.save(test_user)
        print(f"✓ Created test user: {test_user.username}")
    else:
        print(f"✓ Test user already exists: {existing_user.username}")


app.include_router(router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint returning API information"""
    return {
        "message": "Welcome to Habit Gamification API",
        "docs": "/docs",
        "redoc": "/redoc",
    }
