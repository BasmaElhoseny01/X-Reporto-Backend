FROM python:3.9

# Set the working directory
WORKDIR /app

# # Install dependencies
# RUN apt-get update && apt-get install -y \
#     libgl1-mesa-glx \
#     libglib2.0-0 \
#     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Run seeds script first to populate the database then run the FastAPI application
# python -m app.script.seeds , python -m app.main

CMD ["sh", "-c", "python -m app.scripts.seeds && python -m app.main"]
