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
flowchart TD
    A[Sales & Stock Data] --> B[Data Processing Layer]
    B --> C[Forecasting Models]
    C --> D[Inventory Engine]
    D --> E[Streamlit Dashboard]
    E --> F[Purchase Order CSV Export]

---

## 📐 Sequence Diagram  

```mermaid
sequenceDiagram
    participant User as User (Manager)
    participant UI as Streamlit Dashboard
    participant Engine as Inventory Engine
    participant Forecast as Forecasting Model
    participant Output as Purchase Order CSV

    User->>UI: Upload sales.csv, stock.csv, products.csv
    UI->>Forecast: Send sales data for demand forecasting
    Forecast-->>UI: Return demand forecast (7–30 days)
    UI->>Engine: Pass forecast + stock levels
    Engine-->>UI: Calculate reorder point, safety stock, suggested order qty
    UI->>Output: Generate downloadable PO CSV
    Output-->>User: Purchase order ready for export