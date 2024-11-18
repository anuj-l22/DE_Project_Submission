
# Gold Price Prediction Project

This repository contains the complete setup for predicting gold prices using event-driven datasets. The project is containerized with Docker, making it easy to deploy and run.

Watch the project in action:
- **YouTube Demo Video**: [Watch the demo here](https://youtu.be/yfBAJExhg90?si=t-iun44gaLVvZNli)
  
## Getting Started

Follow the steps below to clone and run the project locally using Docker:

### Prerequisites

1. **Docker and Docker-Compose** must be installed on your machine.
   - [Install Docker](https://docs.docker.com/get-docker/)
   - [Install Docker-Compose](https://docs.docker.com/compose/install/)

2. A stable internet connection is required to pull datasets and necessary Docker images.

### Steps to Clone and Run

1. Clone this repository:
   ```bash
   git clone https://github.com/anuj-l22/DE_Project_Submission.git
   cd Project_Submission
   ```

2. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

3. The setup includes the following:
   - A MySQL container initialized with the schema from `MySQL/init.sql`.
   - Event and gold price ETL pipelines running via the `etl` service.
   - App container for additional functionalities (e.g., Streamlit frontend).

4. Access the services:
   - The MySQL database is exposed internally for services and can be accessed at `localhost:3307` to avoid conflicts with the default MySQL port (`3306`).
   - Logs for ETL processing and other services will be visible in the terminal.

### MySQL Credentials

- Default MySQL credentials:
  - **Username**: `root`
  - **Password**: `abcd1234`
- These credentials are hardcoded for internal containers but can be modified if necessary. Update the `docker-compose.yml` and associated configuration files accordingly.

### Requirements

All dependencies are listed in `requirements.txt`. These are automatically installed in the `app` and `etl` containers during the Docker build process. The project uses the following major tools:
- **MySQL** (Database)
- **Python** (ETL pipeline)
- **Docker and Docker-Compose** (Containerization)
- **Streamlit** (Frontend)
- **Public GitHub Repository** (Event data source)

The directory structure in the image aligns with the project organization mentioned. Here's the updated structure reflecting the content more accurately based on the uploaded screenshot:

```plaintext
project-repo/
├── MySQL/
│   ├── README.md       # Nothing added just a placeholder for creating directory
│   ├── init.sql        # Initial schema and data for MySQL
├── app/                # Application logic ( Streamlit)
│   ├── Dockerfile      # Dockerfile for Streamlit app
│   ├── app.py          # Streamlit app logic
│   ├── backend.py      # Backend logic for database and API interaction (yfinance and GitHub)
│   ├── requirements.txt # Dependencies for the app container
│   ├── Gold_Price_Trend.png # visualization/image file for app
│   ├── Types_of_Events.png  # visualization/image file for app
│   ├── README.md       # Nothing added just a placeholder for creating directory
├── etl/                # ETL scripts for fetching and processing data
│   ├── Dockerfile      # Dockerfile for ETL container
│   ├── etl.py          # ETL pipeline script
│   ├── requirements.txt # Dependencies for the ETL container
│   ├── README.md        # Nothing added just a placeholder for creating directory
├── .env                # Environment variables (optional for custom configurations)
├── docker-compose.yml  # Docker-Compose file to set up the environment
├── README.md           # Project overview and instructions
```

### Key Notes:
- The `app` directory contains the Streamlit front-end and backend Python scripts.
- The `etl` directory contains Dockerfile and scripts for the ETL pipeline.
- `.env` is optional but useful for storing environment variables like MySQL credentials and configurations.
- The `docker-compose.yml` orchestrates the setup of the MySQL, app, and ETL containers.

If you need further adjustments or details, let me know!
### Notes

- Ensure you have a stable internet connection for downloading the necessary Docker images and dependencies during the first build.
- If you want to change the default MySQL credentials, update them in:
  - `docker-compose.yml`
  - `MySQL/init.sql` (for any custom schema or user configurations)

### Demo





