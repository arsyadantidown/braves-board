# Permintaan Dukungan Backend — Braves Board

Ringkasan endpoint/model yang dibutuhkan frontend untuk menyelesaikan beberapa
fitur. Disusun oleh tim frontend setelah memeriksa `src/backend/app/api/*`.
Setiap poin menyertakan temuan kondisi saat ini + usulan konkret.

---

## 1. Set `is_completed` pada Task (mark as complete) — blokir fitur #4, #6, #7

**Kondisi sekarang**
- Kolom `is_completed` **sudah ada** di `task_model.py` dan sudah dikembalikan di
  `TaskListResponse` & `TaskDetailResponse`.
- **Tidak ada cara meng-SET-nya lewat API**: `TaskUpdateRequest`
  (`task/schema.py`) tidak memuat `is_completed`, dan `update_task`
  memakai `model_dump(exclude_unset=True)` sehingga field ini tak pernah ikut.
  Tidak ada endpoint khusus mark-complete.

**Yang dibutuhkan** — pilih salah satu (rekomendasi: A, konsisten dengan subtask):

- **A. Endpoint khusus** (mirror `PATCH /subtasks/{id}/complete`):
  ```
  PATCH /api/v1/tasks/{task_id}/complete
  body: { "is_completed": boolean }
  permission: task.update
  response: { id, is_completed, updated_at }
  ```
- **B.** Tambahkan `is_completed: Optional[bool]` ke `TaskUpdateRequest` supaya
  bisa lewat `PATCH /tasks/{task_id}` yang sudah ada.

**Dampak frontend saat siap**: checkbox "selesai" di kartu (tampilan column) +
opsi di card detail, dan Dashboard akan menghitung "Completed" dari
`is_completed` (bukan dari subtask seperti sekarang).

> **STATUS FRONTEND (sudah dipasang, menunggu backend):** UI mark-complete
> sudah dibuat — tombol lingkaran centang di sebelah judul card + kartu hijau
> transparan di column saat `is_completed == true`. Tombolnya **sudah
> memanggil `PATCH /api/v1/tasks/{task_id}/complete` dengan body
> `{ "is_completed": boolean }`** (Opsi A). Selama endpoint belum ada, tombol
> gagal secara sengaja dan menampilkan pesan "menunggu endpoint backend"
> (tidak ada state palsu / localStorage). **Mohon implementasikan Opsi A
> dengan bentuk persis di atas** agar langsung berfungsi tanpa ubah frontend.

---

## 2. Edit / hapus Time Log + konsep "Project" — blokir fitur #8

**Kondisi sekarang**
- `time_tracking/views.py` hanya punya: `start`, `stop`, `ping`, `confirm`,
  `logs` (GET). **Tidak ada** endpoint untuk mengubah/menghapus entry log.
- `TimeLog` **tidak punya `user_id`** → log tidak bisa diatribusikan ke user
  tertentu (frontend saat ini mendekati "log saya" via assignee task).
- **Tidak ada entitas Project.** Struktur data: Board > Column > Task.

**Yang dibutuhkan**

- **Edit time log** (waktu mulai/selesai, tanggal, deskripsi) ala Clockify:
  ```
  PATCH /api/v1/tasks/{task_id}/timer/logs/{log_id}
  body: { "start_time": datetime, "stop_time": datetime|null,
          "activity_description": string|null }
  → duration_seconds dihitung ulang server-side; validasi stop_time > start_time.
  ```
- **Hapus time log**:
  ```
  DELETE /api/v1/tasks/{task_id}/timer/logs/{log_id}
  ```
- **(Opsional) Buat entry manual** (tanpa harus start/stop realtime):
  ```
  POST /api/v1/tasks/{task_id}/timer/logs
  body: { start_time, stop_time, activity_description }
  ```
- **Atribusi user**: tambahkan `user_id` (FK users) ke `TimeLog` agar bisa
  filter/edit "log milik user" dengan benar.
- **Project**: keputusan produk diperlukan. Dua opsi:
  1. Perlakukan **Board sebagai "Project"** (grouping laporan pakai board) —
     tanpa model baru. (Rekomendasi paling murah.)
  2. Tambah entitas **Project** baru (id, name, ...) dan relasi
     Project → Board/Task. Butuh model + endpoint CRUD baru.

---

## 3. Checklist bertingkat ala Trello — blokir fitur #9 (nested)

**Kondisi sekarang**
- `subtask_model.py`: `Subtask` hanya berelasi langsung ke `Task`
  (`task_id`). **Satu tingkat**, tanpa konsep "checklist group".

**Yang dibutuhkan** — struktur dua tingkat: Task → beberapa Checklist → banyak Item.

- **Model baru `Checklist`**:
  ```
  Checklist(id, task_id FK->tasks, title, position, created_at, updated_at, deleted_at)
  ```
- **Item checklist**: tambahkan `checklist_id` (FK->checklists) ke `Subtask`
  (atau model baru `ChecklistItem`), sehingga item berelasi ke Checklist,
  bukan langsung ke Task.
- **Endpoint**:
  ```
  POST   /api/v1/tasks/{task_id}/checklists          { title }
  PATCH  /api/v1/checklists/{checklist_id}           { title }
  DELETE /api/v1/checklists/{checklist_id}
  POST   /api/v1/checklists/{checklist_id}/items     { title }
  PATCH  /api/v1/checklist-items/{item_id}           { title } / complete
  DELETE /api/v1/checklist-items/{item_id}
  ```
- `TaskDetailResponse` sebaiknya mengembalikan `checklists: [{ id, title,
  position, items: [{ id, title, is_completed, position }] }]`.

> Catatan: interaksi "ketik + Enter → simpan & buka input berikutnya" sudah
> diterapkan frontend pada input subtask yang ada sekarang (tidak menunggu ini).

---

## 4. List Task yang di-archive — gap yang ditemukan saat mengerjakan #6

**Kondisi sekarang**
- Endpoint archive/unarchive **sudah ada & dipakai**:
  `PATCH /tasks/{id}/archive` dan `/unarchive`. 👍
- **TAPI** semua endpoint list task memfilter `is_archived == False`
  (`task/repository.py`: `get_all_by_column_id*`, `get_all_by_board_id`), dan
  **tidak ada endpoint untuk melist task yang sudah di-archive**.
- Akibatnya frontend menyimpan daftar archived **di sisi client
  (localStorage)** agar panel "Archived" tetap berfungsi. Ini tidak sinkron
  lintas device dan hilang kalau storage dibersihkan.

**Yang dibutuhkan** — endpoint untuk mengambil task archived, mis.:
```
GET /api/v1/tasks?column_id={id}&archived=true      (tambah query param)
atau
GET /api/v1/boards/{board_id}/tasks/archived
permission: task.view
response: sama seperti TaskListResponse (sudah ada field is_archived)
```
Begitu tersedia, frontend akan memuat daftar archived dari backend (bukan dari
localStorage) sehingga konsisten lintas device.

---

---

## 5. Deadline per Subtask — dibutuhkan untuk fitur #1(b)

**Kondisi sekarang**
- `subtask_model.py` **tidak punya kolom tanggal/deadline** (hanya: id,
  task_id, title, is_completed, position, timestamps).
- `SubtaskCreateRequest` & `SubtaskUpdateRequest` **hanya menerima `title`**.
- Endpoint **update judul subtask SUDAH ADA** (`PATCH /subtasks/{id}` dengan
  `{ title }`) — frontend sudah memakainya untuk edit judul subtask. 👍

**Yang dibutuhkan** agar bisa set & tampilkan deadline per subtask:
- Tambah kolom pada `Subtask`:
  ```
  due_date: Mapped[datetime | None]  (nullable, timezone-aware)
  ```
- Terima `due_date` di request:
  ```
  SubtaskUpdateRequest: due_date: Optional[datetime] = None
  (opsional juga di SubtaskCreateRequest)
  ```
- Kembalikan `due_date` di response subtask (`SubtaskNestedResponse` di
  `task/schema.py` dan response subtask di `subtask/schema.py`).

Begitu tersedia, frontend akan menambahkan date-picker per subtask di card
detail + menampilkan badge deadline (overdue/soon), reuse util
`due-date.util.ts` yang sudah ada.

---

_Sampai poin-poin di atas tersedia, frontend TIDAK menambal (mis. menyimpan
status di client atau menyalahgunakan endpoint lain) sesuai kesepakatan._
