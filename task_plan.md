# 任務管理功能實施計畫

## 1. 系統導航標籤
- 📄 檔案查詢
- 🏠 買家提醒
- 📊 買家提醒(未有excel)
- 💬 WhatsApp
- 📋 業主提醒
- 📅 日曆 (新增)
- ⚙️ 設置

## 2. 搜索結果顯示
- 以檔案編號為唯一識別符
- 顯示完整交易資訊:
  - 本行檔案編號(唯一)
  - 物業地址(可能重複)
  - 客人姓名(可能重複)
  - 聯絡電話(可能重複)
  - 樓價
  - 臨時合約日期
  - 正式合約日期
  - 成交日期

## 3. 任務功能
- 在搜索結果右側添加"任務"按鈕
- 點擊"任務"按鈕時:
  - 顯示任務輸入表單
  - 包含任務內容輸入欄
  - 可選的日期選擇器
  - 可選的時間選擇器
- 如果記錄已有任務,直接在記錄下方顯示

## 4. 日曆頁面(📅)功能
### 月曆視圖
- 顯示所有有日期時間的任務
- 可以點擊日期查看當日任務
- 與Google日曆同步顯示

### 任務列表視圖
- 顯示所有任務
- 可以篩選(全部/有日期/無日期)
- 可以編輯和刪除任務

### 待辦事項列表
- 顯示未設定日期時間的任務
- 可以將待辦事項轉換為日曆事項

## 5. 數據存儲
### SQLite數據庫結構
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_number TEXT NOT NULL,  -- 檔案編號(外鍵)
    content TEXT NOT NULL,      -- 任務內容
    due_date DATE,             -- 到期日期(可為空)
    due_time TIME,             -- 到期時間(可為空)
    created_at DATETIME,       -- 創建時間
    updated_at DATETIME,       -- 更新時間
    status TEXT,              -- 任務狀態
    google_event_id TEXT,      -- Google日曆事件ID
    FOREIGN KEY (file_number) REFERENCES transactions(file_number)
);
```

## 6. Google日曆整合
### 設置需求
- Google Cloud Project
- OAuth 2.0憑證
- 日曆共享權限

### 同步功能
- 當創建/修改/刪除任務時自動同步
- 在Google日曆中顯示:
  - 任務內容
  - 檔案編號
  - 物業地址
  - 客戶資訊

## 7. 權限管理
- 設置Google日曆的共享權限
- 助手可以通過Google日曆查看事項
- 可設置助手是否有編輯權限

## 8. 實施步驟
1. 添加日曆導航標籤
2. 創建日曆頁面
3. 實現任務管理功能
4. 設置SQLite數據庫
5. 整合Google日曆API
6. 實現同步功能
7. 設置權限管理
8. 測試和優化

## 9. 安全性考慮
- API憑證安全存儲
- 敏感資訊的處理
- 數據同步的錯誤處理
- 定期備份機制 