# PlateauBreaker 技術指南：終極作品集版

## 1. 專案概述

PlateauBreaker 是一個全棧健康分析系統，旨在檢測和分析體重高原期。前端採用 Vue3、Vite、PrimeVue、Pinia 和 Chart.js，後端則使用 Python、FastAPI、SQLModel 和 SQLite。系統記錄每日健康數據（體重、睡眠、卡路里、運動），可視化趨勢，使用基於規則的邏輯檢測體重高原期，分析原因，並生成人類可讀的洞察報告。

## 2. 後端架構與精煉

### 2.1 技術棧

- **Python**: 3.11.0rc1
- **FastAPI**: 快速構建 API
- **SQLModel**: 結合 SQLAlchemy 和 Pydantic 的現代化 ORM
- **SQLite**: 輕量級數據庫，便於本地部署和測試

### 2.2 核心服務與規則

- **`health_record_service.py`**: 處理健康記錄的 CRUD 操作，包含重複日期記錄的預防和查詢參數處理。
  - **精煉**: 確保 `timedelta` 等所有必要模組都已在頂部正確導入，並移除冗餘導入。所有時間戳均為 UTC naive，並有明確註釋。移除了未使用的 `status` 導入。
- **`plateau_detector.py`**: 實現基於規則的體重高原期檢測邏輯。分析最近 7 天的體重變化和波動。
  - **精煉**: 統一數據不足時的處理邏輯，確保與 `reason_analyzer.py` 一致，返回 `insufficient_data` 狀態和明確的消息。分析置信度信息已整合。
- **`reason_analyzer.py`**: 分析導致體重高原期的潛在原因，如睡眠不足、卡路里攝入過高、週末飲食過量、運動量減少和數據缺失。每個原因都有權重，並按嚴重程度排序。
  - **精煉**: 統一數據不足時的處理邏輯，確保與 `plateau_detector.py` 一致，返回 `insufficient_data` 狀態和明確的消息。確保數據分區邏輯只執行一次。分析置信度信息已整合。
- **`summary_generator.py`**: 根據高原期狀態和原因分析結果生成人類可讀的摘要和行動建議。
  - **精煉**: 增強摘要的數據驅動性，包含具體數值（如平均睡眠時數、卡路里偏差百分比、週末與平日熱量比、缺失天數）。優化因果層次結構，主因使用強烈措辭，次因使用保守措辭。如果存在數據缺失，則優先顯示置信度警告。

### 2.3 數據庫模型 (`health_record.py`)

- `HealthRecord` 模型包含 `record_date` 的唯一約束，防止重複記錄。
- **精煉**: 增加了關於 UTC naive 時間戳的明確註釋，強調系統範圍內的一致處理。

### 2.4 後端清理與規範

- **導入規範化**: 所有模組中的導入語句都已標準化至頂部，並移除所有未使用的導入。確保一致的導入順序和註釋風格。
- **死代碼移除**: 清理了所有未使用的變數、冗餘賦值和舊版邏輯。
- **UTC 時間戳**: `datetime.utcnow()` 的使用已明確註釋為 UTC naive，確保開發者對時間處理有清晰的理解。

## 3. 前端架構與精煉

### 3.1 技術棧

- **Vue 3 Composition API**: 響應式組件開發
- **Vite**: 極速前端開發構建工具
- **PrimeVue**: 豐富的 UI 組件庫
- **Pinia**: 輕量級狀態管理庫
- **Chart.js**: 數據可視化圖表庫

### 3.2 狀態管理 (`Pinia Stores`)

- **`analytics.ts`**: 負責管理所有分析相關數據，包括儀表板數據、趨勢數據和綜合摘要。將 `summary` 作為分析結論的唯一主要數據源，同時保留 `dashboard` 和 `trends` 作為獨立的數據領域以滿足不同的 UI 職責。
  - **精煉**: 
    - **數據領域劃分**：明確 `dashboard` 用於 KPI，`trends` 用於圖表，`summary` 用於分析結論。`fetchAll` 作為單一入口點，負責加載這三個數據領域。`fetchTrends` 允許獨立調用以支持圖表的時間範圍切換。
    - **Store 結構扁平化**：在 Store 層級暴露 `summaryText`、`summaryStatus`、`primaryCause`、`secondaryCause`、`topReasons` 等扁平化字段，消除組件中 `summary.summary.summary` 的訪問模式。移除了 `reasonsMessage` 和 `reasonsStatus` 等不存在於數據結構中的冗餘計算字段。
    - **類型與 API 對齊**：修復 `api.ts` 與 Store 之間的類型不匹配，移除 UI 主流程中不再需要的 `plateau` 或 `reasons` 獨立狀態，僅保留 `summary` 作為分析數據源。
    - **API 默認值移除**: `analyticsApi` 中的 `reasons` 和 `summary` 方法已移除硬編碼的 `calorieTarget` 默認值，確保所有值都來自 Pinia store。
- **`healthRecords.ts`**: 管理健康記錄的 CRUD 操作和數據列表。維護 `currentQueryParams` 以確保數據刷新的一致性。
  - **精煉**: 
    - **查詢參數持久化**: `loadRecords` 現在調用不帶參數的 `fetchRecords`，以確保 `currentQueryParams`（過濾器狀態）在刷新時不被覆蓋，避免覆寫篩選器。默認查詢參數的初始化邏輯已移至 Store 內部。
    - **加載行為標準化**: CRUD 操作不再直接操縱 `loading` 狀態，而是依賴 `fetchRecords()` 來統一管理。

### 3.3 視圖組件 (`Views`)

- **`Dashboard.vue`**: 顯示關鍵績效指標 (KPIs) 和趨勢圖表。從 `analytics` store 讀取 `dashboard` 和 `trends` 數據，以及 `summary` 數據。
  - **精煉**: 修復了 `summaryData` 的引用錯誤，確保正確使用 `summary` computed property。確保所有數據展示都通過 `analytics` store 的數據流，並正確使用 `calorieTarget`。
- **`Records.vue`**: 提供數據輸入表單和記錄表格。清晰顯示數據集限制。
  - **精煉**: 確保明確且一致地顯示「僅顯示最近 200 條記錄」的提示。移除了 CRUD 操作後對 `loadRecords()` 的重複調用，僅依賴 store 內部的刷新機制。
- **`Analysis.vue`**: 顯示高原期狀態、原因分析和綜合洞察。完全依賴 `analytics` store 的 `summary` 數據。
  - **精煉**: 
    - **數據流統一**: 移除了對 `plateau` 和 `reasons` 的直接調用，完全使用 `analytics` store 中的 `summary` 數據。
    - **卡路里目標統一**: `calorieTarget` 現在完全來自 Pinia store，移除了所有硬編碼的閾值。
    - **加載狀態統一**: `refresh` 函數現在調用 `analyticsStore.fetchAll()`，確保加載狀態的集中管理。

## 4. 代碼質量與專業打磨

- **構建通過性**: 確保 `npm run build` 能夠乾淨地通過，沒有任何錯誤。
- **命名與格式**: 整個代碼庫遵循一致的命名約定和格式規範。
- **模組職責**: 每個模組都遵循單一職責原則，避免引入新的抽象層。
- **可讀性**: 代碼清晰、簡潔，並配有必要的註釋，便於理解和維護。
- **冗餘消除**: 移除了所有重複的數據獲取邏輯和不必要的 `loading` 狀態操作。
- **單一事實來源**: 確保 `calorieTarget` 和分析數據都從 Pinia store 獲取，避免硬編碼和不一致性。

## 5. 部署與運行

### 5.1 後端

1.  進入 `backend` 目錄。
2.  安裝依賴：`pip install -r requirements.txt`
3.  運行數據庫遷移和數據填充：`python seed_data.py` (僅首次運行)
4.  啟動 FastAPI 應用：`uvicorn app.main:app --reload`

### 5.2 前端

1.  進入 `frontend` 目錄。
2.  安裝依賴：`pnpm install` 或 `npm install` 或 `yarn install`
3.  啟動開發伺服器：`pnpm dev` 或 `npm run dev` 或 `yarn dev`

## 6. 結論

此「終極作品集版」的 PlateauBreaker 專案，不僅在功能上完善，更在代碼質量、架構設計和用戶體驗上達到了專業級水準。它展示了對全棧開發的深刻理解，以及將複雜業務邏輯轉化為清晰、可維護代碼的能力，是您 GitHub 作品集的理想選擇。
