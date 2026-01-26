# Sweat - Multiplayer Game Platform

**Sweat** 是一個基於 Python 的網路遊戲平台，實作了完整的 Client-Server 架構。它允許開發者上傳遊戲，玩家下載並在虛擬房間中與朋友連線遊玩。

專案展示了從底層 Socket 通訊、自定義協定設計、到上層 GUI 與多進程遊戲執行的完整整合。

## 🌟 主要功能 (Features)

### 核心系統
- **自定義通訊協定**：基於 TCP 的長度前綴 (Length-prefixed) 封包與 JSON 訊息交換。
- **Session 管理**：支援 Request/Response 同步請求、Event 非同步通知、與 Connection Keep-alive 機制。
- **心跳檢測 (Heartbeat)**：實作雙向健康檢查，Client 主動 Ping，Server 回應 Pong，閒置自動斷線 (Idle Timeout)。

### 遊戲平台功能
- **商店與庫 (Store & Library)**：
    - 開發者可將遊戲打包為 ZIP 上傳。
    - 支援大檔案分塊傳輸 (Chunked Transfer)。
    - 自動下載、驗證雜湊 (Hash Check)、解壓縮安裝。
- **房間系統 (Lobby System)**：
    - 即時更新的房間列表。
    - 支援建立房間、加入房間、權限管理。
- **遊戲啟動 (Game Launcher)**：
    - **獨立進程環境**：遊戲在獨立的 Process 中執行，不影響主程式。
    - **動態注入**：使用 Bootstrapping 技術動態設定 `sys.path`，讓下載的遊戲模組能直接被 import 執行。

### 使用者介面 (GUI)
- 使用 **CustomTkinter** 打造現代化的深色模式介面。
- 頁面切換、即時狀態反饋、錯誤處理提示。

## 🛠️ 技術堆疊 (Tech Stack)

- **語言**: Python 3.10+
- **GUI 框架**: CustomTkinter
- **網路**: Python `socket`, `threading` (Raw TCP implementation)
- **其他依賴**: `Pillow`, `pygame` (範例小遊戲用)

## 📂 專案結構

```text
sweat/
├── client/              # 客戶端程式碼 (GUI, 邏輯控制)
├── server/              # 伺服器程式碼 (Handler, DB, 房間管理)
├── common/              # 共用工具與常數
├── protocol/            # 通訊協定 (Message, Enums, Payloads)
├── session/             # 網路層封裝 (Session, Heartbeat)
├── transport/           # 底層 Socket 處理 (Framing)
├── library/             # [Client] 下載遊戲的存放位置
├── storage/             # [Server] 遊戲檔案與伺服器資料
└── sweat.db             # [Server] 數據庫檔案
```

## 🚀 快速開始 (Getting Started)

### 1. 安裝依賴

建議使用虛擬環境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 啟動伺服器

目前預設伺服器位於linux1.cs.nycu.edu.tw。伺服器預設監聽 `0.0.0.0:14253`。

```powershell
python -m server
# 或指定參數
# python -m server --host 127.0.0.1 --port 8888
```

### 3. 啟動客戶端

啟動 GUI 客戶端連線至伺服器。

```powershell
python -m client
# 或指定參數
# python -m client --host 127.0.0.1
```

## 🎮 開發者指南

### 上傳遊戲
如果你是開發者，可以製作符合規範的 Python 遊戲包，壓縮成 ZIP 檔後透過客戶端上傳。

## 📝 備註 (Notes)

- **Port**: 預設使用 TCP `14253`。
- **資料儲存**: 伺服器目前使用記憶體資料結構暫存房間資訊，遊戲檔案儲存於 `storage/` 目錄。
- **相容性**: 主要於 Windows 環境開發與測試，其他作業系統環境仍在測試階段。

---
*Created as part of the Network Programming Course Project (Fall 2025).*
