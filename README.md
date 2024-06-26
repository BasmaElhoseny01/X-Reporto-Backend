# X-Reporto API

This repository contains the backend implementation for the X-Reporto Web Application.

## Setup

### Prerequisites

1. **PostgreSQL Server**
   - Ensure you have PostgreSQL installed. You can download it from [PostgreSQL Downloads](https://www.postgresql.org/download/).

2. **Python Dependencies**
   - Install required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Environment Variables**

   Create a `.env` file in the app directory with the following variables:

   ```dotenv
   # Example .env file
   DATABASE_URL=postgresql://username:password@localhost/dbname
   SECRET_KEY=your_secret_key_here
   ENV=dev
   PORT=800

4. **Seeds**
   
   Run seeds script 
   ```python
   python -m app.scripts.seeds

5. ***Run Application**
   
   run application main
    ```python
    python -m app.main