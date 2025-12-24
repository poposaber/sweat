# Sweat TCP Client/Server

一個以 Python 實作的簡易 TCP 客戶端/伺服器專案，包含：傳輸層（長度前綴封包）、`Session` 收送迴圈、`protocol` 訊息/JSON 編解碼、伺服器 `dispatcher` 與客戶端 `customtkinter` GUI。

## 需求
- Python 3.10+（使用了 PEP 604 聯集型別 `A | B`）
- Windows/ macOS/ Linux 皆可；Windows 需允許防火牆對本機埠的存取
- 依賴套件：`customtkinter`

## 安裝
建議使用虛擬環境（若已建立 `.venv` 可跳過）：

```powershell
# 建立並啟用虛擬環境（Windows PowerShell）
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安裝依賴
pip install -r requirements.txt
```

## 快速開始
- 啟動伺服器（內含簡易 CLI，可輸入 `status` 或 `quit`）：
```powershell
python -m server --host 127.0.0.1 --port 14253
```
- 另開新終端啟動客戶端 GUI（預設連線到上述位址）：
```powershell
python -m client --host 127.0.0.1 --port 14253
```

## 測試（目前為簡易直跑腳本）
```powershell
python tests\protocol\roundtrip_auth.py
python tests\server\dispatcher_roundtrip.py
```
說明：以上腳本使用 `assert` 直接驗證協定編解碼與伺服器分派。未採用 pytest；後續可升級為 `pytest -q`。

## 專案結構
- `client/`：客戶端核心（`client.py`、`client_controller.py`、`client_gui.py`、`ui/login_page.py`）
- `server/`：伺服器（`server.py`、`dispatcher.py`、`handlers/auth.py`、`infra/acceptor.py`、`__main__.py`）
- `protocol/`：訊息模型與編解碼（`message.py`、`json_codec.py`、`enums.py`、`payloads/*`）
- `session/`：`Session` 抽象與背景接收迴圈（`session.py`）
- `transport/`：TCP framing 與錯誤（`framed_socket.py`、`errors.py`）
- `tests/`：輕量測試腳本

## 重要檔案導覽
- 伺服器入口：`server/__main__.py`（CLI）
- 客戶端入口：`client/__main__.py`（GUI）
- 協定編解碼：`protocol/json_codec.py`、`protocol/message.py`、`protocol/enums.py`
- 傳輸封包：`transport/framed_socket.py`
- 會話與收送：`session/session.py`

## 常見問題
- 埠占用：若 14253 已被占用，請改用 `--port` 指定其他埠。
- 防火牆：首次啟動伺服器時，Windows 可能提示防火牆授權，請允許本機連線。
- `customtkinter` 未安裝：請先執行 `pip install -r requirements.txt`。

## 後續建議（規劃）
- 將現有直跑測試遷移至 pytest。
- 在 `client/api/auth.py` 將 `register()` 統一改用 `request_response()`。
- 在 `server/dispatcher.py` 移除流程 `assert`，改為明確錯誤處理。
- README 加入架構圖與更完整的協定文件（若需要）。
