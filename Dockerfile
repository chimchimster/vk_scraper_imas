FROM python:3.10-slim
WORKDIR .
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . vk_scraper_imas
CMD ["python3", "vk_scraper_imas/app.py"]