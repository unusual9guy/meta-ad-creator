# 1. Start with a lightweight Python base image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy your requirements file first (for caching efficiency)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your app code
COPY . .

# 6. Expose the port Streamlit runs on
EXPOSE 8501

# 7. The command to run the app
CMD ["streamlit", "run", "src/app.py"]