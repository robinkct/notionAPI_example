# Notion API 整合工具

這個專案提供了一個簡單且強大的 Python 工具包，用於與 Notion API 進行互動。支持數據庫操作、頁面管理、屬性處理以及圖片上傳等功能。

## 功能特點

- 數據庫操作
  - 創建新數據庫
  - 添加/更新數據庫屬性
  - 查詢數據庫內容
  - 支持多種過濾條件
  - 支持排序功能

- 頁面管理
  - 創建新頁面
  - 更新頁面內容
  - 添加關聯屬性
  - 批量操作頁面

- 圖片處理
  - 支持外部圖片 URL
  - 支持本地圖片上傳（通過 Imgur）
  - 支持圖片說明文字

- 屬性處理
  - 支持多種屬性類型（文本、數字、選擇、多選、日期等）
  - 格式化屬性值輸出
  - 關聯屬性支持

## 安裝

1. 克隆專案：
```bash
git clone https://github.com/your-username/notion-api-tool.git
cd notion-api-tool
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

## 配置

1. 在專案根目錄創建 `.env` 文件：
```env
NOTION_TOKEN=your_notion_token
IMGUR_CLIENT_ID=your_imgur_client_id
```

2. 獲取必要的認證：
   - Notion Token: 從 [Notion Developers](https://developers.notion.com/) 獲取
   - Imgur Client ID: 從 [Imgur API](https://api.imgur.com/oauth2/addclient) 獲取

## 專案結構 