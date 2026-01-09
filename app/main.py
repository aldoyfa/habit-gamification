from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="Habit Gamification API",
    description="""
## Habit Gamification API

API untuk mengelola habit tracking dengan fitur gamifikasi.

### Features

* **Create Habits** - Buat habit baru dengan judul dan deskripsi
* **Track Progress** - Lacak progres penyelesaian habit
* **Streak Tracking** - Hitung streak berturut-turut
* **Complete/Miss** - Tandai habit sebagai selesai atau terlewat

### Domain Model

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

app.include_router(router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint returning API information"""
    return {
        "message": "Welcome to Habit Gamification API",
        "docs": "/docs",
        "redoc": "/redoc",
    }
