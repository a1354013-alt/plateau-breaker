# PlateauBreaker: AI 體重高原期分析系統 (終極作品集版)

![PlateauBreaker Hero Image](./frontend/src/assets/hero.png)

## 專案概述

PlateauBreaker 是一個全棧健康分析系統，旨在幫助用戶檢測、理解並克服體重高原期。它結合了現代前端技術與強大的後端分析能力，提供個性化的健康洞察和行動建議。本專案的「終極作品集版」經過多輪精煉，在代碼質量、架構設計和用戶體驗上均達到專業級水準，是展示全棧開發能力的理想選擇。

### 核心功能

-   **每日健康數據記錄**：輕鬆記錄體重、睡眠時數、卡路里攝入、運動分鐘數等關鍵指標。
-   **趨勢可視化**：直觀的圖表展示體重、睡眠、卡路里等數據的長期趨勢。
-   **智能高原期檢測**：採用基於規則的邏輯，自動識別體重高原期。
-   **原因深度分析**：分析導致高原期的潛在原因，如睡眠不足、卡路里超標、週末飲食過量、運動量減少或數據缺失。
-   **數據驅動的洞察**：生成人類可讀的摘要，包含具體數值證據和可操作的個性化建議。
-   **響應式設計**：在不同設備上提供流暢一致的用戶體驗。

## 技術棧

### 後端 (Backend)

-   **Python**: 3.11.0rc1
-   **FastAPI**: 高性能、易於學習、快速開發的 Web 框架。
-   **SQLModel**: 結合 SQLAlchemy 和 Pydantic 的現代化非同步 ORM，用於數據庫交互。
-   **SQLite**: 輕量級數據庫，便於本地開發和部署。
-   **核心分析模組**: `plateau_detector.py`, `reason_analyzer.py`, `summary_generator.py`。

### 前端 (Frontend)

-   **Vue 3 Composition API**: 漸進式 JavaScript 框架，用於構建響應式用戶界面。
-   **Vite**: 極速前端開發構建工具，提供快速冷啟動和即時熱模塊更新。
-   **PrimeVue**: 豐富的 Vue UI 組件庫，提供美觀且功能強大的組件。
-   **Pinia**: 輕量級、類型安全的 Vue 狀態管理庫，用於管理應用程序狀態。
-   **Chart.js**: 靈活的 JavaScript 圖表庫，用於數據可視化。

## 專案結構

```
PlateauBreaker/
├── backend/                      # 後端服務
│   ├── app/                      # FastAPI 應用
│   │   ├── api/                  # API 路由定義
│   │   ├── database.py           # 數據庫連接與初始化
│   │   ├── models/               # SQLModel 數據模型
│   │   ├── rules/                # 核心業務邏輯 (高原期檢測、原因分析、摘要生成)
│   │   ├── schemas/              # Pydantic 數據驗證模型
│   │   └── services/             # 數據庫操作服務
│   ├── requirements.txt          # Python 依賴
│   └── seed_data.py              # 數據庫種子數據 (用於初始化)
├── frontend/                     # 前端應用
│   ├── public/                   # 靜態資源
│   ├── src/                      # 源代碼
│   │   ├── assets/               # 圖片、圖標等靜態資源
│   │   ├── components/           # 可重用 Vue 組件
│   │   ├── router/               # Vue Router 配置
│   │   ├── services/             # API 服務調用
│   │   ├── stores/               # Pinia 狀態管理模塊
│   │   └── views/                # 頁面組件 (Dashboard, Records, Analysis)
│   ├── index.html                # 入口 HTML 文件
│   ├── package.json              # 前端依賴
│   └── vite.config.ts            # Vite 配置
├── .gitignore
├── README.md                     # 專案說明 (此文件)
└── PlateauBreaker_Technical_Guide.md # 詳細技術指南
```

## 快速開始

### 1. 克隆專案

```bash
git clone https://github.com/your-username/PlateauBreaker.git
cd PlateauBreaker
```

### 2. 後端設置

```bash
cd backend
pip install -r requirements.txt
python seed_data.py  # 首次運行，初始化數據庫並填充示例數據
uvicorn app.main:app --reload
```

後端服務將在 `http://127.0.0.1:8000` 啟動。您可以在瀏覽器中訪問 `http://127.0.0.1:8000/docs` 查看 API 文檔。

### 3. 前端設置

打開新的終端窗口：

```bash
cd frontend
pnpm install  # 或者使用 npm install / yarn install
pnpm dev      # 或者使用 npm run dev / yarn dev
```

前端應用將在 `http://localhost:5173` 啟動。

## 核心精煉亮點 (終極作品集版)

本版本在以下方面進行了全面優化，以達到專業級作品集標準：

1.  **數據流統一**：Dashboard 和 Analysis 頁面完全依賴 `analytics` Pinia Store 中的 `summary` 數據，確保單一數據源和邏輯一致性。
2.  **加載狀態穩定化**：所有數據加載狀態由 `analytics` Store 的 `fetchAll()` 集中管理，避免 UI 狀態不一致。
3.  **查詢參數持久化**：`healthRecords` Store 在 CRUD 操作後自動使用 `currentQueryParams` 刷新數據，保持用戶視圖不變。
4.  **分析邏輯對齊**：`plateau_detector` 和 `reason_analyzer` 在數據不足時的處理邏輯保持一致，並在 `summary_generator` 中優先顯示數據置信度警告。
5.  **增強摘要洞察**：`summary_generator` 輸出包含具體數值（如平均睡眠時數、卡路里偏差百分比、週末與平日熱量比、缺失天數）的詳細洞察。
6.  **簡化數據訪問**：Pinia Store 中的 Computed Helpers 徹底消除了深層嵌套的數據訪問模式。
7.  **卡路里目標統一**：`calorieTarget` 完全由 Pinia Store 管理，所有視圖和 API 調用均使用此單一來源，移除硬編碼閾值。
8.  **後端代碼清理**：標準化所有導入，移除死代碼，並為 UTC naive 時間戳添加明確註釋。
9.  **專業級代碼質量**：遵循一致的命名、格式和模組職責，確保代碼清晰、可讀且易於維護。

## 貢獻

歡迎提出問題和建議。如果您發現任何問題或有改進意見，請隨時提交 Issue 或 Pull Request。

## 許可證

此專案根據 MIT 許可證發布。詳情請參閱 `LICENSE` 文件。

--- 

**PlateauBreaker** — 您的智能體重管理夥伴。
