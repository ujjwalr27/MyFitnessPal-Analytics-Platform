# MyFitnessPal CSV to Grafana

A web application that accepts CSV exports from MyFitnessPal, processes the data, stores it in PostgreSQL, and visualizes key metrics through Grafana dashboards.

## Overview

This project simplifies data archival and insight generation for MyFitnessPal users by providing:

- A web interface to upload CSV exports
- Data validation and transformation
- Secure PostgreSQL storage
- Interactive Grafana dashboards for visualization

## Features

- **CSV Upload**: Simple web form to upload MyFitnessPal CSV exports
- **Data Processing**: Backend validation and transformation of nutrition data
- **PostgreSQL Storage**: Optimized schema for time-series fitness data
- **Grafana Integration**: Pre-configured dashboards for calories, macronutrients, and exercise analysis
- **Containerized**: Easy deployment with Docker Compose

## Technical Stack

- **Backend**: Python with Flask
- **Database**: PostgreSQL 
- **Data Processing**: Pandas and SQLAlchemy
- **Frontend**: HTML, Bootstrap, and JavaScript
- **Visualization**: Grafana
- **Containerization**: Docker and Docker Compose

## Prerequisites

- Docker and Docker Compose
- MyFitnessPal account with CSV export capability

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/myfitnessapp.git
cd myfitnessapp
```

### 2. Configure Environment (Optional)

You can modify the environment variables in `docker-compose.yml` if needed.

### 3. Launch the Application

```bash
docker-compose up -d
```

This will start three containers:
- Flask application (port 5000)
- PostgreSQL database (port 5432)
- Grafana (port 3000)

### 4. Access the Applications

- **Web Interface**: http://localhost:5000
- **Grafana Dashboards**: http://localhost:3001 (login with admin/admin)

## Using the Application

1. Export your nutrition data from MyFitnessPal as CSV
2. Visit the web interface at http://localhost:5000
3. Upload output CSV file 
4. After successful upload, view your data in Grafana

Please select 1-09-2014 to 31-09-2014 to see visualizations for September 2014. Change users to see different users data.

## Grafana Dashboards

The application includes pre-configured dashboards for:

- Daily caloric intake
- Macronutrient breakdown (carbs, protein, fat)
- Nutritional trends over time



### Project Structure

```
myfitnessapp/
├── backend/                 # Flask application
│   ├── app.py               # Main application entry
│   ├── config.py            # Configuration settings
│   ├── requirements.txt     # Python dependencies
│   ├── utils/               # Utility modules
│   └── routes/              # API endpoints
├── frontend/                # Web interface
│   ├── static/              # CSS, JS, and other assets
│   └── templates/           # HTML templates
├── grafana/                 # Grafana configuration
│   ├── dashboards/          # Dashboard definitions
│   └── datasources/         # Data source configurations
├── docker-compose.yml       # Container orchestration
└── Dockerfile               # Flask app container
```

## Security Considerations

- The application uses basic authentication for Grafana
- Database credentials are stored in environment variables
- File uploads are validated for type and size

## Troubleshooting

**Database Connection Issues:**
- Ensure PostgreSQL container is running
- Check database credentials in docker-compose.yml

**CSV Import Errors:**
- Verify your CSV is a valid MyFitnessPal export
- Check that required columns are present (Date, Calories, Carbs, Fat, Protein)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- MyFitnessPal for providing exportable nutrition data
- Grafana for the visualization platform
- The Flask and PostgreSQL communities for excellent documentation 