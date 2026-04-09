# 食譜收藏夾系統 — 流程圖文件

> 版本：1.0  
> 日期：2026-04-09  
> 依據：[PRD.md](./PRD.md)、[ARCHITECTURE.md](./ARCHITECTURE.md)

---

## 1. 使用者流程圖（User Flow）

### 1.1 整體操作流程

```mermaid
flowchart LR
    A([使用者開啟網頁]) --> B[首頁]
    B --> C{已登入？}

    C -->|否| D{要執行什麼？}
    D -->|瀏覽食譜| E[食譜列表頁]
    D -->|搜尋食譜| F[搜尋功能]
    D -->|註冊帳號| G[註冊頁]
    D -->|登入| H[登入頁]

    G --> H
    H --> B

    C -->|是| I{要執行什麼操作？}
    I -->|瀏覽食譜| E
    I -->|搜尋食譜| F
    I -->|新增食譜| J[新增食譜表單]
    I -->|查看收藏| K[個人收藏頁]
    I -->|個人資料| L[個人資料頁]
    I -->|管理後台| M[管理員後台]
    I -->|登出| B

    E --> N[食譜詳情頁]
    F --> E

    N --> O{要執行什麼操作？}
    O -->|收藏| P[加入收藏夾]
    O -->|編輯| Q[編輯食譜表單]
    O -->|刪除| R[確認刪除]
    O -->|返回列表| E

    P --> N
    Q --> N
    R --> E

    J --> N
    K --> N
```

### 1.2 註冊與登入流程

```mermaid
flowchart LR
    A([使用者]) --> B{有帳號？}

    B -->|否| C[前往註冊頁]
    C --> D[填寫帳號/密碼/暱稱]
    D --> E{驗證通過？}
    E -->|是| F[註冊成功，導向登入頁]
    E -->|否| G[顯示錯誤訊息]
    G --> D

    B -->|是| H[前往登入頁]
    F --> H
    H --> I[輸入帳號/密碼]
    I --> J{登入成功？}
    J -->|是| K[導向首頁]
    J -->|否| L[顯示錯誤訊息]
    L --> I
```

### 1.3 新增食譜流程

```mermaid
flowchart LR
    A([已登入使用者]) --> B[點擊新增食譜]
    B --> C[填寫基本資訊]
    C --> D["輸入食譜名稱、描述"]
    D --> E["選擇分類標籤、難度"]
    E --> F[設定烹飪時間]
    F --> G[新增食材清單]
    G --> H["逐一輸入食材（名稱/數量/單位）"]
    H --> I{還有食材？}
    I -->|是| H
    I -->|否| J[新增烹飪步驟]
    J --> K["逐一輸入步驟（編號/說明）"]
    K --> L{還有步驟？}
    L -->|是| K
    L -->|否| M[上傳封面圖片]
    M --> N[預覽食譜]
    N --> O{確認送出？}
    O -->|是| P[儲存至資料庫]
    O -->|否| C
    P --> Q[導向食譜詳情頁]
```

### 1.4 搜尋食譜流程

```mermaid
flowchart LR
    A([使用者]) --> B[輸入搜尋關鍵字]
    B --> C{需要篩選？}
    C -->|是| D[選擇篩選條件]
    D --> E["分類 / 難度 / 烹飪時間"]
    E --> F[送出搜尋]
    C -->|否| F
    F --> G{有搜尋結果？}
    G -->|是| H[顯示食譜列表]
    G -->|否| I[顯示無結果提示]
    I --> B
    H --> J[點選食譜]
    J --> K[食譜詳情頁]
```

### 1.5 收藏食譜流程

```mermaid
flowchart LR
    A([已登入使用者]) --> B[瀏覽食譜詳情頁]
    B --> C{已收藏？}
    C -->|否| D[點擊收藏按鈕]
    D --> E[加入收藏夾]
    E --> F[按鈕變為已收藏狀態]
    C -->|是| G[點擊取消收藏]
    G --> H[從收藏夾移除]
    H --> I[按鈕變為未收藏狀態]
```

### 1.6 管理員操作流程

```mermaid
flowchart LR
    A([管理員登入]) --> B[管理員後台]
    B --> C{要管理什麼？}

    C -->|食譜管理| D[食譜管理列表]
    D --> E{執行什麼操作？}
    E -->|編輯| F[編輯食譜表單]
    E -->|刪除| G[確認刪除對話框]
    F --> D
    G --> D

    C -->|使用者管理| H[使用者管理列表]
    H --> I{執行什麼操作？}
    I -->|停用帳號| J[確認停用]
    I -->|檢視資料| K[使用者詳情]
    J --> H
    K --> H
```

---

## 2. 系統序列圖（Sequence Diagram）

### 2.1 使用者註冊

```mermaid
sequenceDiagram
    actor User as 👤 使用者
    participant Browser as 🌐 瀏覽器
    participant Flask as ⚙️ Flask Route
    participant Model as 📊 Model
    participant DB as 🗄️ SQLite

    User->>Browser: 點擊「註冊」
    Browser->>Flask: GET /auth/register
    Flask-->>Browser: 回傳註冊頁面 HTML

    User->>Browser: 填寫帳號、密碼、暱稱，按下送出
    Browser->>Flask: POST /auth/register
    Flask->>Flask: 驗證表單資料
    alt 驗證失敗
        Flask-->>Browser: 回傳錯誤訊息
    else 驗證成功
        Flask->>Flask: 密碼雜湊 (hash)
        Flask->>Model: User.create(username, hashed_pw, nickname)
        Model->>DB: INSERT INTO users
        DB-->>Model: 成功
        Model-->>Flask: 回傳 User 物件
        Flask-->>Browser: 302 重導向至 /auth/login
    end
```

### 2.2 使用者登入

```mermaid
sequenceDiagram
    actor User as 👤 使用者
    participant Browser as 🌐 瀏覽器
    participant Flask as ⚙️ Flask Route
    participant Model as 📊 Model
    participant DB as 🗄️ SQLite

    User->>Browser: 點擊「登入」
    Browser->>Flask: GET /auth/login
    Flask-->>Browser: 回傳登入頁面 HTML

    User->>Browser: 輸入帳號、密碼，按下送出
    Browser->>Flask: POST /auth/login
    Flask->>Model: User.query(username)
    Model->>DB: SELECT * FROM users WHERE username=?
    DB-->>Model: 回傳使用者資料
    Model-->>Flask: 回傳 User 物件

    Flask->>Flask: check_password_hash(password)
    alt 密碼錯誤
        Flask-->>Browser: 回傳錯誤訊息
    else 密碼正確
        Flask->>Flask: login_user(user)
        Flask-->>Browser: 302 重導向至首頁
    end
```

### 2.3 新增食譜

```mermaid
sequenceDiagram
    actor User as 👤 使用者
    participant Browser as 🌐 瀏覽器
    participant Flask as ⚙️ Flask Route
    participant Model as 📊 Model
    participant DB as 🗄️ SQLite

    User->>Browser: 點擊「新增食譜」
    Browser->>Flask: GET /recipes/new
    Flask->>Flask: 檢查登入狀態
    Flask-->>Browser: 回傳新增食譜表單 HTML

    User->>Browser: 填寫食譜資料，按下送出
    Browser->>Flask: POST /recipes/new
    Flask->>Flask: 驗證表單資料

    Flask->>Model: Recipe.create(title, description, ...)
    Model->>DB: INSERT INTO recipes
    DB-->>Model: 回傳 recipe_id

    loop 每一個食材
        Flask->>Model: Ingredient.create(recipe_id, name, qty, unit)
        Model->>DB: INSERT INTO ingredients
    end

    loop 每一個步驟
        Flask->>Model: Step.create(recipe_id, order, description)
        Model->>DB: INSERT INTO steps
    end

    DB-->>Model: 全部成功
    Model-->>Flask: 回傳 Recipe 物件
    Flask-->>Browser: 302 重導向至 /recipes/{id}
    Browser-->>User: 顯示食譜詳情頁
```

### 2.4 搜尋食譜

```mermaid
sequenceDiagram
    actor User as 👤 使用者
    participant Browser as 🌐 瀏覽器
    participant Flask as ⚙️ Flask Route
    participant Model as 📊 Model
    participant DB as 🗄️ SQLite

    User->>Browser: 輸入關鍵字、選擇篩選條件
    Browser->>Flask: GET /search?q=關鍵字&category=中式&difficulty=簡單
    Flask->>Model: Recipe.search(keyword, filters)
    Model->>DB: SELECT * FROM recipes WHERE title LIKE ? AND ...
    DB-->>Model: 回傳符合條件的食譜
    Model-->>Flask: 回傳 Recipe 列表
    Flask-->>Browser: 回傳搜尋結果 HTML
    Browser-->>User: 顯示食譜列表
```

### 2.5 收藏 / 取消收藏

```mermaid
sequenceDiagram
    actor User as 👤 使用者
    participant Browser as 🌐 瀏覽器
    participant Flask as ⚙️ Flask Route
    participant Model as 📊 Model
    participant DB as 🗄️ SQLite

    User->>Browser: 點擊收藏按鈕（❤️）
    Browser->>Flask: POST /favorites/{recipe_id}
    Flask->>Flask: 檢查登入狀態

    Flask->>Model: Favorite.query(user_id, recipe_id)
    Model->>DB: SELECT * FROM favorites WHERE user_id=? AND recipe_id=?
    DB-->>Model: 回傳結果

    alt 尚未收藏
        Flask->>Model: Favorite.create(user_id, recipe_id)
        Model->>DB: INSERT INTO favorites
        DB-->>Model: 成功
        Flask-->>Browser: 回傳 {"status": "favorited"}
    else 已收藏
        Flask->>Model: Favorite.delete(user_id, recipe_id)
        Model->>DB: DELETE FROM favorites WHERE ...
        DB-->>Model: 成功
        Flask-->>Browser: 回傳 {"status": "unfavorited"}
    end

    Browser-->>User: 更新收藏按鈕狀態
```

### 2.6 管理員刪除食譜

```mermaid
sequenceDiagram
    actor Admin as 🛡️ 管理員
    participant Browser as 🌐 瀏覽器
    participant Flask as ⚙️ Flask Route
    participant Model as 📊 Model
    participant DB as 🗄️ SQLite

    Admin->>Browser: 點擊「刪除」按鈕
    Browser->>Browser: 彈出確認對話框
    Admin->>Browser: 確認刪除

    Browser->>Flask: DELETE /admin/recipes/{id}
    Flask->>Flask: 檢查管理員權限

    Flask->>Model: Ingredient.delete_by_recipe(recipe_id)
    Model->>DB: DELETE FROM ingredients WHERE recipe_id=?
    Flask->>Model: Step.delete_by_recipe(recipe_id)
    Model->>DB: DELETE FROM steps WHERE recipe_id=?
    Flask->>Model: Favorite.delete_by_recipe(recipe_id)
    Model->>DB: DELETE FROM favorites WHERE recipe_id=?
    Flask->>Model: Recipe.delete(recipe_id)
    Model->>DB: DELETE FROM recipes WHERE id=?

    DB-->>Model: 全部刪除成功
    Model-->>Flask: 成功
    Flask-->>Browser: 302 重導向至管理列表
    Browser-->>Admin: 顯示更新後的食譜列表
```

---

## 3. 功能清單對照表

| # | 功能 | URL 路徑 | HTTP 方法 | 說明 |
|---|------|----------|-----------|------|
| 1 | 首頁 | `/` | GET | 顯示推薦食譜、最新食譜、搜尋入口 |
| 2 | 使用者註冊 | `/auth/register` | GET / POST | 顯示註冊表單 / 處理註冊 |
| 3 | 使用者登入 | `/auth/login` | GET / POST | 顯示登入表單 / 處理登入 |
| 4 | 使用者登出 | `/auth/logout` | GET | 登出並清除 Session |
| 5 | 食譜列表 | `/recipes` | GET | 顯示所有食譜列表 |
| 6 | 食譜詳情 | `/recipes/<id>` | GET | 顯示食譜完整資訊（食材 + 步驟） |
| 7 | 新增食譜 | `/recipes/new` | GET / POST | 顯示新增表單 / 處理新增 |
| 8 | 編輯食譜 | `/recipes/<id>/edit` | GET / POST | 顯示編輯表單 / 處理編輯 |
| 9 | 刪除食譜 | `/recipes/<id>/delete` | POST | 刪除指定食譜 |
| 10 | 搜尋食譜 | `/search` | GET | 依關鍵字與篩選條件搜尋 |
| 11 | 收藏食譜 | `/favorites/<recipe_id>` | POST | 收藏 / 取消收藏（toggle） |
| 12 | 收藏清單 | `/favorites` | GET | 顯示個人收藏的食譜清單 |
| 13 | 個人資料 | `/profile` | GET / POST | 顯示 / 編輯個人資料 |
| 14 | 管理員儀表板 | `/admin` | GET | 管理員後台首頁 |
| 15 | 管理食譜 | `/admin/recipes` | GET | 管理所有食譜清單 |
| 16 | 管理員刪除食譜 | `/admin/recipes/<id>/delete` | POST | 管理員刪除任意食譜 |
| 17 | 管理使用者 | `/admin/users` | GET | 管理所有使用者清單 |
| 18 | 停用使用者 | `/admin/users/<id>/toggle` | POST | 停用 / 啟用使用者帳號 |
