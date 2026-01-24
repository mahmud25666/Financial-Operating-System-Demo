# Financial-Operating-System-Demo
# 📊 Financial Operating System (FOS) for Hardware Infrastructure

### Automating Capital Flow for Engineering Fleets & Real-World Assets (RWA)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://financial-operating-system-demo-ysdocfpbevor9xhd93xzn4.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.12-blue) ![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Project Overview
Legacy ERP systems are often too rigid for the rapid deployment cycles of decentralized infrastructure (DePIN) and EV mobility networks. 

I built this **Financial Operating System (FOS)** as a modular, Python-native engine to bridge the gap between **physical engineering milestones** and **financial ledgering**. It is designed to manage high-velocity capital allocation for hardware procurement, installation, and maintenance.

**Live Demo:** [Click Here to Launch App](https://financial-operating-system-demo-ysdocfpbevor9xhd93xzn4.streamlit.app/)

---

## ⚙️ Key Features
* **🔄 Automated Ledger Synchronization:**
    * Eliminates manual data entry errors. The system automatically rebuilds an audit-ready `Master_Ledger` in Excel (`.xlsx`) every time a transaction occurs.
    * Supports multi-entity architecture (automatically generates separate ledger tabs for distinct business units).
* **⏳ Dual-Date Timestamping:**
    * Implements "Transaction Date" (Banking) vs. "System Entry Date" (Operations) logic to ensure precise audit trails and compliance.
* **📈 Real-Time Velocity Visualization:**
    * **Burn-Down Charts:** Track project budget consumption against hardware deployment.
    * **Net Cash Flow:** Combo charts visualizing monthly inflows vs. outflows.
    * **Risk Analysis:** Automated "Overpayment" detection and "Outstanding Debt" flags.
* **📂 Intelligent Parsing:**
    * Integrated PDF parsing pipeline to extract invoice metadata automatically.

---

## 🛠️ Tech Stack
* **Core Logic:** Python 3.12
* **Frontend:** Streamlit
* **Visualization:** Plotly Interactive Graphs
* **Data Engine:** Pandas, OpenPyXL (Advanced Excel Automation)
* **Deployment:** Streamlit Community Cloud

---

## 🚀 How to Run Locally

1. **Clone the repository**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/Financial-Operating-System-Demo.git](https://github.com/YOUR_USERNAME/Financial-Operating-System-Demo.git)
   cd Financial-Operating-System-Demo
2. **Install Dependencies**
   pip install -r requirements.txt

3. **Run the Application**
   streamlit run app.py
   
🔮 Future Roadmap (DePIN Integration)
This FOS is the foundational layer for a larger DePIN Architecture. Upcoming modules include:

Phase 2: IoT Sensor Integration (Ingesting live telemetry from EV chargers).

Phase 3: On-Chain Settlements (Triggering USDC payments based on hardware uptime).

Phase 4: Geospatial Fleet Map (QGIS integration for node visualization).
