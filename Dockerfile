FROM python:3.9-slim

# Install necessary packages
RUN apt-get update \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy the application code to the container
COPY app /app

# Expose Streamlit port
EXPOSE 8505

# Run both cron and Streamlit
CMD /usr/bin/python3 -m streamlit run /app/app.py --server.port 8505
