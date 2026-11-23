# 1. Base image: Python pehle se installed
FROM python:3.12-slim

# 2. Container ke andar kaam karne ka folder
WORKDIR /app

# 3. Pehle sirf requirements copy karein (caching k liye)
COPY requirements.txt .

# 4. Packages install karein
RUN pip install --no-cache-dir -r requirements.txt

# 5. Baqi poora code copy karein
COPY . .

# 6. Port batayein
EXPOSE 8000

# 7. App chalane ki command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]