
# Gold Price Prediction Project

This repository contains the complete setup for predicting gold prices using event-driven datasets. The project is containerized with Docker, making it easy to deploy and run.

## Getting Started

Follow the steps below to clone and run the project locally using Docker:

### Prerequisites

1. **Docker and Docker-Compose** must be installed on your machine.
   - [Install Docker](https://docs.docker.com/get-docker/)
   - [Install Docker-Compose](https://docs.docker.com/compose/install/)
2. A **GitHub Personal Access Token** is required to pull the events data stored on a private GitHub repository.

### Steps to Clone and Run

1. Clone this repository:
   ```bash
   git clone https://github.com/anuj-l22/DE_Project_Submission.git
   cd Project_Submission
   ```

2. **Update the `.env` file**:
   - Add your GitHub token to the `.env` file:
     ```
     GITHUB_TOKEN=your_github_token
     ```
   - **Note**: The default MySQL credentials for the internal container are:
     - Username: `root`
     - Password: `abcd1234`
   - These can be changed if required by updating the `docker-compose.yml` file and corresponding scripts.

3. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

4. The setup includes the following:
   - MySQL container initialized with the schema from `MySQL/init.sql`.
   - Event and gold price ETL pipelines running via the `etl` service.
   - App container for additional functionalities (e.g., Streamlit frontend).

5. Access the services:
   - The MySQL database is exposed internally for services and can be accessed at `localhost:3307` if required as local MySQL uses 3306 so in Docker I am using 3307 to avoid discrepancies
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
- **GitHub API** (Event data source)

### Directory Structure

```
project-repo/
├── MySQL/
│   ├── README.md       # Instructions for MySQL setup
│   ├── init.sql        # Initial schema and data for MySQL
├── app/                # Application logic (e.g., Streamlit)
├── etl/                # ETL scripts for fetching and processing data
├── .env                # Environment variables (e.g., GitHub token)
├── docker-compose.yml  # Docker-Compose file to set up the environment
├── README.md           # This file
```

### Notes

- Ensure you have a stable internet connection for downloading the necessary Docker images and dependencies during the first build.
- If you want to change the default MySQL credentials, update them in:
  - `docker-compose.yml`
  - `MySQL/init.sql` (for any custom schema or user configurations)

### Troubleshooting

1. **GitHub Token Issues**:
   - If the pipeline fails to fetch data from the GitHub repository, verify that the `GITHUB_TOKEN` is correct and has sufficient permissions.
   
2. **MySQL Connection Issues**:
   - Ensure no other MySQL instance is running on the same port (default: 3306).

3. **Docker Build Errors**:
   - Try rebuilding the images:
     ```bash
     docker-compose down
     docker-compose up --build
     ```

4. For further questions or issues, raise an issue in this repository.

---

Enjoy exploring gold price predictions!
```


