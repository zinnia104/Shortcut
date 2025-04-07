# 檔案管理系統 (File Management System)

這是一個基於 Flask 的檔案管理系統，用於處理和查詢房地產相關的檔案資料。

## 功能特點

### 1. 檔案查詢功能
- 檔案編號查詢
- 電話號碼查詢
- 客戶名稱查詢
- 物業地址查詢

### 2. 買家提醒功能
- 自動計算律師費
- 自動計算進一步按金
- 自動計算契據費
- 支持手動調整費用
- 複製買家提醒內容

### 3. 檔案上傳功能
- 支持 Excel 檔案上傳
- 自動讀取檔案內容
- 保存檔案配置

## 技術架構

### 後端
- Python 3.13.1
- Flask 框架
- Pandas 數據處理
- OpenPyXL Excel 處理

### 前端
- HTML5
- CSS3
- JavaScript
- 響應式設計

### 打包工具
- PyInstaller 6.12.0

## 開發計劃

### 第一階段（已完成）
- [x] 基礎架構搭建
- [x] 檔案查詢功能
- [x] 買家提醒功能
- [x] Excel 檔案上傳
- [x] 應用程序打包

### 第二階段（計劃中）
- [ ] 用戶認證系統
- [ ] 數據庫整合
- [ ] 檔案版本控制
- [ ] 批量處理功能
- [ ] 報表生成功能

### 第三階段（計劃中）
- [ ] 多語言支持
- [ ] 主題定制
- [ ] API 文檔
- [ ] 性能優化
- [ ] 自動更新功能

## 安裝說明

1. 環境要求
   - Windows 10 或更高版本
   - Python 3.13.1
   - 必要的 Python 套件（見 requirements.txt）

2. 安裝步驟
   ```bash
   # 創建虛擬環境
   python -m venv venv
   
   # 啟動虛擬環境
   .\venv\Scripts\activate
   
   # 安裝依賴
   pip install -r requirements.txt
   ```

3. 運行應用
   ```bash
   # 開發模式
   python server.py
   
   # 或使用打包版本
   cd dist/Shortcut
   ./Shortcut.exe
   ```

## 目錄結構

```
project/
├── server.py          # 後端服務器
├── index.html         # 前端界面
├── styles.css         # 樣式文件
├── config.json        # 配置文件
├── shortcut.spec      # PyInstaller 配置
├── requirements.txt   # 依賴列表
├── uploads/          # 上傳文件目錄
├── build/           # 構建目錄
└── dist/            # 發布目錄
```

## 注意事項

1. 檔案安全
   - 定期備份上傳的檔案
   - 注意檔案權限設置
   - 避免敏感信息洩露

2. 性能優化
   - 大檔案處理優化
   - 查詢性能優化
   - 內存使用優化

3. 維護建議
   - 定期清理臨時文件
   - 監控系統日誌
   - 更新依賴套件

## 貢獻指南

1. Fork 本專案
2. 創建特性分支
3. 提交更改
4. 發起 Pull Request

## 授權說明

本專案採用 MIT 授權條款 