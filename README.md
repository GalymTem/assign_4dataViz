# assign_4dataViz
# Database & Monitoring Dashboard (PostgreSQL + Prometheus + Grafana)

This project implements a monitoring environment for PostgreSQL and simulated weather data using Prometheus and Grafana.  
It includes:
- PostgreSQL database
- Prometheus for metrics collection
- Node Exporter for system metrics
- PostgreSQL Exporter for DB metrics
- Custom Python Weather Exporter (simulated or via OpenWeather API)
- Grafana for visualization

---

## Setup Instructions

### Start All Services

```bash
docker-compose up -d
```

Services included:

| Service | Port | Description |
|----------|------|-------------|
| PostgreSQL | 5432 | Database instance |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3000 | Dashboard visualization |
| Node Exporter | 9100 | System metrics |
| PostgreSQL Exporter | 9187 | Database metrics |
| Weather Exporter | 8000 | Custom Python exporter |

To verify containers are running:
```bash
docker ps
```

---

## Prometheus Configuration (`prometheus.yml`)

Prometheus scrapes metrics from all exporters every 10 seconds:

```yaml
global:
  scrape_interval: 10s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["prometheus:9090"]

  - job_name: "node_exporter"
    static_configs:
      - targets: ["node_exporter:9100"]

  - job_name: "postgres_exporter"
    static_configs:
      - targets: ["postgres_exporter:9187"]

  - job_name: "weather_exporter"
    static_configs:
      - targets: ["host.docker.internal:8000"]
```

Check targets here:  
[http://localhost:9090/targets](http://localhost:9090/targets)

All jobs should show as **UP**.

---

## Weather Exporter

A custom Python script that simulates weather data (or pulls from OpenWeather if API key is set).

**Run manually:**
```bash
python weather_exporter.py
```

Exposes metrics at:  
[http://localhost:8000/metrics](http://localhost:8000/metrics)

Example output:
```
weather_temp_celsius{city="Astana"} 12.3
weather_humidity_percent{city="Astana"} 47.5
weather_wind_speed_ms{city="Astana"} 3.9
weather_cloudiness_percent{city="Astana"} 55
```

If no API key is set, random realistic weather values are generated automatically.

---

## Grafana Dashboard

Access Grafana at:  
[http://localhost:3000](http://localhost:3000)

Default login:
```
user: admin
password: admin
```

You can create panels to visualize:
- PostgreSQL query stats
- CPU, RAM, and disk usage
- Weather temperature, humidity, and wind speed

Use Prometheus as your **data source**:
```
URL: http://prometheus:9090
```

Then, add panels with queries like:
```promql
weather_temp_celsius{city="Astana"}
weather_humidity_percent{city="Astana"}
weather_wind_speed_ms{city="Astana"}
```

---

## Export Dashboard

After creating your dashboard:
1. Go to **Dashboard settings (⚙️)** → **JSON Model**
2. Click **Download JSON**
3. Save as `database_dashboard.json`

---

## Verification Checklist

All containers running  
Prometheus shows all targets as **UP**  
Weather metrics visible at `/metrics`  
Grafana connected to Prometheus  
Dashboard displays metrics correctly  

---

## Useful Commands

Restart all containers:
```bash
docker-compose down && docker-compose up -d
```

View container logs:
```bash
docker logs <container_name>
```

Stop containers:
```bash
docker-compose down
```

---

## Author

**Student:** _Your Name_  
**Course:** _Database Systems / Monitoring Assignment_  
**Institution:** Astana IT University  
**Instructor:** _Your Instructor’s Name_

---

**Included Files:**
- `docker-compose.yml`
- `prometheus.yml`
- `custom-ex.py`
- `database_dashboard`
- `README.md`
- `grafana.db`

---

<!--
TODO (for later):

### Global Filter
Create a dashboard variable:
- Go to Dashboard settings → Variables → Add Variable
- Name: `city`
- Query: `label_values(weather_temp_celsius, city)`
- Use `$city` in all queries:
  ```promql
  weather_temp_celsius{city="$city"}
  ```

### Alert Rule
Create alert rule:
- Go to Alerting → Alert Rules → New alert rule
- Expression:
  ```promql
  weather_temp_celsius{city="$city"} > 30
  ```
- Condition: `WHEN last() OF query (A, 5m, now) IS ABOVE 30`
- Set notification channel
-->
