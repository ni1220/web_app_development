# 食譜收藏夾系統 — 路由設計文件（Routes）

> 版本：1.0
> 日期：2026-04-16
> 依據：[PRD.md](./PRD.md)、[ARCHITECTURE.md](./ARCHITECTURE.md)、[DB_DESIGN.md](./DB_DESIGN.md)

---

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|-----------|----------|----------|------|
| 首頁 | GET | `/` | `index.html` | 顯示推薦食譜、最新食譜、搜尋入口 |
| **-- 認證（Auth）--** | | | | |
| 顯示登入頁 | GET | `/auth/login` | `auth/login.html` | 顯示登入表單 |
| 處理登入 | POST | `/auth/login` | — | 驗證帳密，成功導向首頁 |
| 顯示註冊頁 | GET | `/auth/register` | `auth/register.html` | 顯示註冊表單 |
| 處理註冊 | POST | `/auth/register` | — | 建立帳號，成功導向登入頁 |
| 登出 | GET | `/auth/logout` | — | 清除 Session，導向首頁 |
| **-- 食譜（Recipe）--** | | | | |
| 食譜列表 | GET | `/recipes` | `recipe/list.html` | 顯示所有食譜，含搜尋與篩選 |
| 食譜詳情 | GET | `/recipes/<id>` | `recipe/detail.html` | 顯示單筆食譜（食材 + 步驟） |
| 顯示新增食譜頁 | GET | `/recipes/new` | `recipe/create.html` | 顯示新增食譜表單 |
| 處理新增食譜 | POST | `/recipes/new` | — | 儲存食譜至 DB，導向詳情頁 |
| 顯示編輯食譜頁 | GET | `/recipes/<id>/edit` | `recipe/edit.html` | 顯示編輯表單（預填資料） |
| 處理編輯食譜 | POST | `/recipes/<id>/edit` | — | 更新 DB，導向詳情頁 |
| 刪除食譜 | POST | `/recipes/<id>/delete` | — | 刪除食譜，導向食譜列表 |
| **-- 搜尋（Search）--** | | | | |
| 搜尋食譜 | GET | `/search` | `recipe/list.html` | 依關鍵字與篩選條件搜尋 |
| **-- 收藏（Favorite）--** | | | | |
| 個人收藏列表 | GET | `/favorites` | `favorite/list.html` | 顯示使用者收藏的食譜 |
| 切換收藏狀態 | POST | `/favorites/<recipe_id>` | — | 收藏或取消收藏（toggle），回傳 JSON |
| **-- 個人資料（Profile）--** | | | | |
| 個人資料頁 | GET | `/profile` | `profile/index.html` | 顯示個人資料 |
| 更新個人資料 | POST | `/profile` | — | 更新暱稱/密碼，導向個人資料頁 |
| **-- 管理員後台（Admin）--** | | | | |
| 管理員儀表板 | GET | `/admin` | `admin/dashboard.html` | 顯示系統統計數據 |
| 管理食譜列表 | GET | `/admin/recipes` | `admin/recipes.html` | 顯示所有食譜，供管理員操作 |
| 管理員刪除食譜 | POST | `/admin/recipes/<id>/delete` | — | 管理員刪除任意食譜 |
| 管理使用者列表 | GET | `/admin/users` | `admin/users.html` | 顯示所有使用者 |
| 切換使用者帳號狀態 | POST | `/admin/users/<id>/toggle` | — | 停用或啟用使用者帳號 |

---

## 2. 路由詳細說明

### Blueprint: `auth` — 認證模組（`/auth`）

#### `GET /auth/login` — 顯示登入頁
- **輸入**：無
- **邏輯**：若已登入，重導向至首頁
- **輸出**：渲染 `auth/login.html`
- **錯誤處理**：無

#### `POST /auth/login` — 處理登入
- **輸入**（表單欄位）：`username`, `password`
- **邏輯**：
  1. 取得 `User.get_by_username(username)`
  2. 驗證 `check_password_hash(user.password_hash, password)`
  3. 呼叫 `login_user(user)`（Flask-Login）
- **輸出**：成功 → 重導向 `/`；失敗 → 回傳錯誤訊息至 `auth/login.html`
- **錯誤處理**：帳號不存在或密碼錯誤 → 顯示「帳號或密碼錯誤」

#### `GET /auth/register` — 顯示註冊頁
- **輸入**：無
- **邏輯**：若已登入，重導向至首頁
- **輸出**：渲染 `auth/register.html`
- **錯誤處理**：無

#### `POST /auth/register` — 處理註冊
- **輸入**（表單欄位）：`username`, `password`, `nickname`
- **邏輯**：
  1. 驗證表單欄位不為空
  2. 確認 `username` 尚未被使用
  3. `generate_password_hash(password)` 產生密碼雜湊
  4. 呼叫 `User.create(username, password_hash, nickname)`
- **輸出**：成功 → 重導向 `/auth/login`；失敗 → 回傳錯誤至 `auth/register.html`
- **錯誤處理**：帳號已存在 → 顯示「帳號已被使用」

#### `GET /auth/logout` — 登出
- **輸入**：無
- **邏輯**：呼叫 `logout_user()`（Flask-Login）
- **輸出**：重導向 `/`
- **錯誤處理**：無

---

### Blueprint: `recipe` — 食譜模組（`/recipes`）

#### `GET /recipes` — 食譜列表
- **輸入**（URL 參數，可選）：`category`, `difficulty`
- **邏輯**：呼叫 `Recipe.get_all()` 或帶篩選條件查詢
- **輸出**：渲染 `recipe/list.html`，傳入食譜列表
- **錯誤處理**：無結果時顯示空狀態提示

#### `GET /recipes/<int:id>` — 食譜詳情
- **輸入**（URL 參數）：`id`（食譜 ID）
- **邏輯**：
  1. `Recipe.get_by_id(id)`，不存在則 404
  2. 取得 `recipe.ingredients`、`recipe.steps`
  3. 若已登入，查詢 `Favorite.query_favorite(user_id, id)` 確認收藏狀態
- **輸出**：渲染 `recipe/detail.html`
- **錯誤處理**：食譜不存在 → 404 頁面

#### `GET /recipes/new` — 顯示新增食譜頁
- **輸入**：無
- **邏輯**：需已登入（`@login_required`）
- **輸出**：渲染 `recipe/create.html`
- **錯誤處理**：未登入 → 重導向 `/auth/login`

#### `POST /recipes/new` — 處理新增食譜
- **輸入**（表單欄位）：`title`, `description`, `difficulty`, `cook_time`, `category`, `cover_image`（檔案），以及多筆 `ingredient[name]`, `ingredient[quantity]`, `ingredient[unit]`，以及多筆 `step[order]`, `step[description]`
- **邏輯**：
  1. 驗證必填欄位（`title`）
  2. 若有上傳圖片，儲存至 `static/uploads/`
  3. `Recipe.create(...)` 建立食譜
  4. 逐一 `Ingredient.create(...)` 建立食材
  5. 逐一 `Step.create(...)` 建立步驟
- **輸出**：成功 → 重導向 `/recipes/<新食譜 id>`；失敗 → 回傳錯誤
- **錯誤處理**：title 為空 → 顯示驗證錯誤

#### `GET /recipes/<int:id>/edit` — 顯示編輯食譜頁
- **輸入**（URL 參數）：`id`
- **邏輯**：
  1. `@login_required`
  2. `Recipe.get_by_id(id)`
  3. 驗證目前使用者是作者或管理員
- **輸出**：渲染 `recipe/edit.html`，預填現有資料
- **錯誤處理**：食譜不存在 → 404；無權限 → 403

#### `POST /recipes/<int:id>/edit` — 處理編輯食譜
- **輸入**（表單欄位）：同新增表單
- **邏輯**：
  1. 更新 `recipe.update(...)`
  2. 刪除舊的食材與步驟，重新建立
- **輸出**：成功 → 重導向 `/recipes/<id>`
- **錯誤處理**：同上

#### `POST /recipes/<int:id>/delete` — 刪除食譜
- **輸入**（URL 參數）：`id`
- **邏輯**：
  1. `@login_required`
  2. 驗證使用者是作者或管理員
  3. `recipe.delete()`（cascade 刪除子資料）
- **輸出**：重導向 `/recipes`
- **錯誤處理**：食譜不存在 → 404；無權限 → 403

---

### Blueprint: `search` — 搜尋模組（`/search`）

#### `GET /search` — 搜尋食譜
- **輸入**（URL 查詢參數）：`q`（關鍵字）, `category`, `difficulty`
- **邏輯**：呼叫 `Recipe.search(keyword, filters)`
- **輸出**：渲染 `recipe/list.html`，傳入搜尋結果
- **錯誤處理**：無結果 → 顯示「找不到符合的食譜」

---

### Blueprint: `favorite` — 收藏模組（`/favorites`）

#### `GET /favorites` — 個人收藏列表
- **輸入**：無
- **邏輯**：
  1. `@login_required`
  2. `Favorite.get_by_user(current_user.id)` 取得收藏清單
- **輸出**：渲染 `favorite/list.html`
- **錯誤處理**：未登入 → 重導向 `/auth/login`

#### `POST /favorites/<int:recipe_id>` — 切換收藏狀態
- **輸入**（URL 參數）：`recipe_id`
- **邏輯**：
  1. `@login_required`
  2. 查詢 `Favorite.query_favorite(user_id, recipe_id)`
  3. 若存在 → `Favorite.delete_favorite(...)` 取消收藏
  4. 若不存在 → `Favorite.create(...)` 新增收藏
- **輸出**：JSON `{"status": "favorited"}` 或 `{"status": "unfavorited"}`
- **錯誤處理**：食譜不存在 → 404

---

### Blueprint: `profile` — 個人資料模組（`/profile`）

#### `GET /profile` — 個人資料頁
- **輸入**：無
- **邏輯**：`@login_required`，取得 `current_user` 資料
- **輸出**：渲染 `profile/index.html`
- **錯誤處理**：未登入 → 重導向 `/auth/login`

#### `POST /profile` — 更新個人資料
- **輸入**（表單欄位）：`nickname`（必填）, `password`（可選）, `confirm_password`（可選）
- **邏輯**：
  1. 更新 nickname
  2. 若有填寫 `password`，驗證兩次密碼相同後更新
- **輸出**：成功 → 重導向 `/profile`；失敗 → 顯示錯誤
- **錯誤處理**：兩次密碼不符 → 顯示驗證錯誤

---

### Blueprint: `admin` — 管理員後台（`/admin`）

> 所有 admin 路由皆需要 `@login_required` 與 `@admin_required` 裝飾器。

#### `GET /admin` — 管理員儀表板
- **輸入**：無
- **邏輯**：統計食譜總數、使用者總數、最新食譜
- **輸出**：渲染 `admin/dashboard.html`

#### `GET /admin/recipes` — 管理食譜列表
- **輸入**：無
- **邏輯**：`Recipe.get_all()` 取得所有食譜（含作者資訊）
- **輸出**：渲染 `admin/recipes.html`

#### `POST /admin/recipes/<int:id>/delete` — 管理員刪除食譜
- **輸入**（URL 參數）：`id`
- **邏輯**：直接刪除任意食譜
- **輸出**：重導向 `/admin/recipes`

#### `GET /admin/users` — 管理使用者列表
- **輸入**：無
- **邏輯**：`User.get_all()` 取得所有使用者
- **輸出**：渲染 `admin/users.html`

#### `POST /admin/users/<int:id>/toggle` — 切換使用者帳號狀態
- **輸入**（URL 參數）：`id`
- **邏輯**：取得使用者後，切換 `is_active` 欄位
- **輸出**：重導向 `/admin/users`

---

## 3. Jinja2 模板清單

| 模板路徑 | 繼承自 | 說明 |
|----------|--------|------|
| `base.html` | — | 全站基礎模板（導覽列、頁尾、CSS/JS） |
| `index.html` | `base.html` | 首頁（推薦食譜 + 搜尋入口） |
| `auth/login.html` | `base.html` | 登入頁 |
| `auth/register.html` | `base.html` | 註冊頁 |
| `recipe/list.html` | `base.html` | 食譜列表頁（也用於搜尋結果） |
| `recipe/detail.html` | `base.html` | 食譜詳情頁（食材 + 步驟 + 收藏按鈕） |
| `recipe/create.html` | `base.html` | 新增食譜表單 |
| `recipe/edit.html` | `base.html` | 編輯食譜表單 |
| `favorite/list.html` | `base.html` | 個人收藏清單頁 |
| `profile/index.html` | `base.html` | 個人資料頁 |
| `admin/dashboard.html` | `base.html` | 管理員儀表板 |
| `admin/recipes.html` | `base.html` | 管理食譜清單 |
| `admin/users.html` | `base.html` | 管理使用者清單 |
| `errors/404.html` | `base.html` | 404 頁面 |
| `errors/403.html` | `base.html` | 403 頁面 |
