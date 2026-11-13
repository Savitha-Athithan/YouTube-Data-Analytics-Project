# YouTube Data Harvesting, Warehousing & Business Analytics

## Project Overview

This project focuses on collecting YouTube channel and video data using the YouTube Data API, storing the extracted information in MongoDB, transferring data into MySQL, and analysing it through an interactive Streamlit application.

## Technologies Used

- Python
- YouTube Data API v3
- MongoDB Atlas
- MySQL
- Streamlit
- Pandas
- Plotly
- Python libraries: PyMongo, mysql-connector-python, isodate

## Key Features

- Retrieve YouTube channel information.
- Collect video details and statistics.
- Store extracted data in MongoDB Atlas.
- Migrate data into MySQL tables.
- Perform SQL queries for business analysis.
- Display results through an interactive Streamlit dashboard.

## Dashboard Screenshots

### Main Dashboard
![youtube](screenshots/Screenshot%20youtube%20data.png)


### Channel Information
![youtube](screenshots/Screenshot%20youtube.png)


### Video Analytics



## How to Run the Project

1. Clone or download this repository.

2. Install the required libraries:

   `pip install -r requirements.txt`

3. Create a `.env` file in the project folder.

4. Add your own API key and MongoDB connection string:

   `YOUTUBE_API_KEY=your_api_key`

   `MONGODB_URI=your_mongodb_connection_string`

5. Ensure your MySQL database is running and configured.

6. Start the application:

   `python -m streamlit run youtube.py`

## Learning Outcomes

- Working with API-based data extraction.
- Handling data using MongoDB and MySQL.
- Writing SQL queries for data analysis.
- Building interactive dashboards using Streamlit.
- Understanding data storage and retrieval workflows.

## Project Type

Data Science Course Capstone Project – GUVI, India
