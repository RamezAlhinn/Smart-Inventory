# Smart Inventory Management System  

AI-powered platform for **demand forecasting, stock optimization, and automated purchase order generation**.  
Built to help supermarkets, pharmacies, and retailers reduce waste, prevent stockouts, and improve cash flow.  

---

## 📌 Overview  
This system ingests historical **sales and stock data**, applies forecasting models (Moving Average, Prophet), and calculates **reorder points** with safety stock. The output is a **purchase order recommendation** displayed in a web dashboard, with the option to export results.  

The architecture is **modular** and can be extended to other verticals (e.g., pharmacies, e-commerce, distribution).  

---

## ✨ Features  
- CSV-based ingestion for sales, stock, and products  
- Time-series demand forecasting: **Moving Average (fast)**, **Prophet (advanced)**  
- Safety stock and reorder point calculation  
- Automated purchase order generation with MOQ support  
- Interactive **Streamlit dashboard** for managers  
- Extensible package design for future ML models and integrations  

---

## 🛠 Tech Stack  
- **Language:** Python  
- **Core Libraries:** Pandas, NumPy, Streamlit, Prophet  
- **Architecture:** Modular packages (forecasting, inventory, utils)  
- **Visualization:** Streamlit Charts  

---

## 🏗 Architecture  

```mermaid
sequenceDiagram
    participant User
    participant UI as Dashboard
    participant Engine as InventoryEngine
    participant Forecast as ForecastModel
    participant Output as PurchaseOrderCSV

    User->>UI: Upload sales.csv, stock.csv, products.csv
    UI->>Forecast: Send sales data for demand forecasting
    Forecast-->>UI: Return demand forecast (7–30 days)
    UI->>Engine: Pass forecast + stock levels
    Engine-->>UI: Calculate reorder point, safety stock, suggested order qty
    UI->>Output: Generate downloadable PO CSV
    Output-->>User: Purchase order ready for export


## 🚀 Deployment with Docker & GitHub Actions

Our app is fully containerized and auto-updates when code is pushed to **GitHub → Docker Hub → Server**.

### 1. Build & Push (GitHub Actions)  
Every push to `main` triggers a GitHub Action that:  
- Builds the Docker image  
- Tags it as `latest`  
- Pushes it to Docker Hub (`ramezalhinn000/smart-inventory:latest`)  

### 2. Run the App Locally / Server  
Start the container:  
```bash
docker run -d \
  --name smart-inventory \
  -p 8501:8501 \
  -v "$PWD/data:/app/data" \
  ramezalhinn000/smart-inventory:latest
```

- `-p 8501:8501` → exposes the Streamlit dashboard  
- `-v "$PWD/data:/app/data"` → mounts local data folder into the container  

### 3. Auto-Updates with Watchtower  
Install **Watchtower** to auto-pull new images and restart the app:  
```bash
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --interval 60 \
  smart-inventory
```

- `--interval 60` → checks every 60 seconds for new images  
- If a new image is found, Watchtower pulls it, stops the old container, and restarts it with the updated image.  

### 4. Logs & Monitoring  
Check logs for Watchtower:  
```bash
docker logs watchtower
```

### 5. (Optional) Restart Policy  
To ensure containers always restart after reboot:  
```bash
docker update --restart unless-stopped smart-inventory
docker update --restart unless-stopped watchtower
```

---

⚡ Now your app is **self-updating**: push code → GitHub → Docker Hub → Server updates automatically.