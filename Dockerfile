FROM python3.10-slim
WORKDIR .
COPY .. requirements.txt
CMD pip install -r requirements.txt --no-cahce-dir
COPY vk_scraper_imas .
CMD ["python3", "vk_scarper_imas/app.py"]