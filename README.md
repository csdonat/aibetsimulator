# AI Bet Simulator

Football betting analysis system with data collection and visualization.

## Display App

### On local computer
```bash
cd display_app
streamlit run main.py
```

### Easyest using docker-compose
```bash
docker compose up -d
docker compose down
```

## Collector Pipeline

### Full Season Collection
Collect all data for a complete season:
```bash
cd collector_pipeline
python main.py --league 39 --season 2025
```

### Automated full season Collection
Collect all data for all seasons
```bash
cd collector_pipeline
./run_pipeline.sh
```

### Backfill / Recovery run
Collect all data between now and a desired date.
```bash
cd collector_pipeline
./run_backfill.sh --from 2026-02-28
```

### Daily Collection (for a specific date)
Collect data for a specific date and merge with existing:
```bash
cd collector_pipeline
python main.py --league 39 --season 2025 --date 2025-03-01
```

### Automated Daily Collection (multiple leagues)
Configure leagues in `run_daily.sh`, then:
```bash
cd collector_pipeline
./run_daily.sh                    # Collects yesterday's data
./run_daily.sh --date 2025-03-01  # Specific date
```

Set up cron for daily automation (runs at 2 AM):
```bash
crontab -e
# Add: 0 2 * * * /path/to/collector_pipeline/run_daily.sh >> /path/to/logs/daily.log 2>&1
```
