# 📈 Monitoring Guide

> *Set up metrics, logs, and alerts to track your trading system*

## 🛠️ Prerequisites

- Prometheus server
- Grafana
- Access to application logs in `logs/`

## 🔍 Metrics Export

1. The application exposes Prometheus metrics on port `8000` by default.
2. Configure Prometheus to scrape:
   ```yaml
   scrape_configs:
     - job_name: 'trading_system'
       static_configs:
         - targets: ['localhost:8000']
   ```

## 📊 Grafana Dashboards

1. Import our sample dashboard JSON into Grafana (file: `monitoring/grafana_dashboard.json`).
2. Key panels:
   - **Tick Latency**: p50/p99 latency of tick processing
   - **Signal Rate**: Signals generated per minute
   - **Order Errors**: Failed order count

## 📝 Log Aggregation

- Logs are written to `logs/trading.log` in JSON format.
- To centralize logs, forward to a log collector (e.g., Loki, ELK):
  ```bash
  # Example using promtail (Loki client)
  promtail --config.file=promtail-config.yaml
  ```

## 🚨 Alerting

1. Create Prometheus alerts:
   ```yaml
   alert: HighTickLatency
   expr: tick_latency_p99 > 0.02
   for: 1m
   labels:
     severity: warning
   annotations:
     summary: "High tick processing latency"
     description: "p99 > 20ms"
   ```
2. Configure Alertmanager for email or Slack notifications.

---

*Monitoring gives you confidence and early warnings if something goes wrong.* 