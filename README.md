# Display App


## On local computer

```bash
streamlit run main.py
```

## On VPS using docker
```bash
docker build -t betwai-streamlit .
docker run -d --name betwai-streamlit --restart=always -p 8501:8501 betwai-streamlit
```

# Collector pipeline

```bash
python main.py --league 39 --season 2025
```
