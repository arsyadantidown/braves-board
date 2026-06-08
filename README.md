# Braves Board Backend

Backend API untuk aplikasi manajemen tugas (Task Tracker) Braves Board. Dibangun menggunakan arsitektur modern berkinerja tinggi berbasis *Domain-Driven Design* (DDD) yang dirancang agar kompatibel dengan lingkungan Serverless Google Cloud Platform (GCP).

## Teknologi Utama

* **Framework:** FastAPI (Python 3.11)
* **Database Relasional:** PostgreSQL 15 (via asyncpg & SQLAlchemy 2.0)
* **In-Memory Database / Cache:** Redis 7 (Untuk manajemen *hot data* seperti pelacakan durasi Timer hibrida)
* **Cloud Storage:** Google Cloud Storage (GCS) untuk lampiran file
* **Migrasi Database:** Alembic (Asynchronous)
* **Observability:** Prometheus & Grafana
* **Kontainerisasi:** Docker & Docker Compose

---

## Persyaratan Sistem (Prerequisites)

Sebelum memulai, pastikan Anda telah menginstal aplikasi berikut di mesin lokal Anda:

1. Docker Desktop (atau Docker Engine & Docker Compose)
2. Git

*(Catatan: Anda tidak perlu menginstal Python atau PostgreSQL secara lokal di OS Anda karena semuanya sudah diisolasi di dalam Docker).*

---

## Struktur Proyek Utama

Proyek ini telah direstrukturisasi agar lebih modular dan mudah dipelihara:

* `deploy/` : Berisi konfigurasi infrastruktur (Dockerfile, Docker Compose untuk Dev/Prod/Staging).
* `src/backend/app/api/` : Direktori utama kode sumber yang dipisahkan berdasarkan domain/fitur (auth, board, task, time_tracking, dll).
* `src/backend/app/config/` : Tempat menyimpan *environment variables* (`.env`) dan kredensial JSON.
* `src/backend/db_migrations/` : Folder konfigurasi dan riwayat migrasi Alembic.

---

## Cara Menjalankan Proyek di Lokal

### 1. Kloning Repositori & Setup Environment

Kloning repositori ini ke mesin lokal Anda:

git clone <url-repositori-anda>
cd braves-board-backend

Buat file *environment variables* (`.env`) di dalam folder `src/backend/app/config/env/`. Karena aplikasi ini mendukung berbagai jenis environment, **terdapat 4 file konfigurasi** yang perlu disiapkan, yaitu:

1. `development.env` (untuk *development* lokal)
2. `test.env` (untuk *automated testing*)
3. `staging.env` (untuk *server staging*)
4. `production.env` (untuk *server production*)

Anda dapat menyalin *template* awal dari file `env.example` yang sudah disediakan:

```bash
cd src/backend/app/config/env/
cp env.example development.env
cp env.example test.env
cp env.example staging.env
cp env.example production.env
```

Pastikan Anda mengubah isi variabel di dalam file-file tersebut (seperti `POSTGRES_USER`, `JWT_SECRET`, dll) sesuai dengan *environment* yang dituju. Docker Compose akan secara otomatis mendeteksi dan menggunakan file konfigurasi yang tepat sesuai dengan file `.yml` yang dijalankan.
---

### 2. Jalankan Kontainer Docker

Karena file `docker-compose` berada di folder `deploy/compose/`, Anda harus menggunakan *flag* `-f` untuk menunjuk ke file yang benar saat menjalankannya.

Jalankan perintah berikut di root repositori:

```bash
docker-compose -f deploy/compose/docker-compose.dev.yml up -d --build
```

Tunggu beberapa saat hingga proses *build* dan instalasi *dependencies* Python selesai.

---

### 3. Verifikasi Layanan (Akses URL)

Jika semua kontainer berstatus "Up", Anda bisa mengakses berbagai layanan berikut melalui browser:

* **API Swagger UI (Docs):** http://localhost:8000/docs
* **API ReDoc:** http://localhost:8000/redoc
* **pgAdmin (Manajemen Database):** http://localhost:8080

  * *Email:* [admin@bangunindo.com](mailto:admin@bangunindo.com)
  * *Password:* admin
  * *(Hubungkan server DB dengan Host: `db`, Username: `postgres`, Password: `postgres`)*
* **RedisInsight (Manajemen Redis):** http://localhost:5540
* **Grafana (Monitoring Metrics):** http://localhost:3000 (User/Pass: admin/admin)

---

## Manajemen Database (Alembic Migrations)

Aplikasi ini menggunakan layanan terpisah (`migrator`) untuk mengeksekusi migrasi database secara terisolasi.

### 1. Menerapkan Migrasi (Upgrade ke Head)

Untuk menjalankan semua file migrasi yang ada dan memperbarui struktur tabel di PostgreSQL, jalankan *service* `migrator`. *Script* `migrator.sh` akan otomatis mengeksekusi `alembic upgrade head`.

```bash
docker-compose -f deploy/compose/docker-compose.dev.yml up migrator
````

*(Catatan: Kontainer `migrator` akan otomatis berhenti (exit) setelah proses migrasi selesai. Ini adalah perilaku normal).*

---

### 2. Daftarkan Model Baru di `env.py`

Setiap kali Anda membuat model baru di `src/backend/app/models/`, Anda WAJIB mengimpornya ke dalam file `src/backend/db_migrations/env.py` agar terdeteksi oleh Alembic:

```python
from app.models.nama_file_baru import NamaModelBaru
```

---

### 3. Membuat File Migrasi Baru (Autogenerate)

Setelah model didaftarkan atau diubah, buat skrip migrasinya dengan mengeksekusi perintah di dalam kontainer `api`:

```bash
docker-compose -f deploy/compose/docker-compose.dev.yml exec api alembic revision --autogenerate -m "nama_perubahan_anda"
```

*(Setelah file migrasi terbentuk, jalankan kembali langkah 1 (`up migrator`) untuk menerapkannya ke database).*

---

### 4. Membatalkan Migrasi Terakhir (Downgrade)

Jika perlu rollback migrasi, jalankan perintah berikut melalui kontainer `api`:

```bash
docker-compose -f deploy/compose/docker-compose.dev.yml exec api alembic downgrade -1
```
---

## Perintah Operasional Docker Lainnya

**Melihat Log Aplikasi Backend (Real-time):**

```bash
docker-compose -f deploy/compose/docker-compose.dev.yml logs -f api
```

**Restart Hanya Backend (Misal setelah merubah .env):**

```bash
docker-compose -f deploy/compose/docker-compose.dev.yml restart api
```

**Mematikan Seluruh Kontainer:**

```bash
docker-compose -f deploy/compose/docker-compose.dev.yml down
```

**Mematikan Kontainer & Menghapus Semua Data (Hard Reset Database & Redis):**

```bash
docker-compose -f deploy/compose/docker-compose.dev.yml down -v
```

*(Hati-hati: Perintah ini akan menghapus seluruh data lokal di PostgreSQL, Redis, dan Grafana Anda yang ada di Docker Volume).*

```
```
