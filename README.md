AI Job Market Analytics Dashboard

A Django-based web application that provides real-time insights into the global AI and tech job market — including salary trends, market growth, and job satisfaction scores. Built as the final project for the Software Construction and Development (SCD) laboratory course.

Live Demo: scd-lab-final-project.vercel.app


Features


User authentication (register, login, logout)
Interactive dashboard with AI/tech job market analytics
Salary insights and market growth visualizations
Job satisfaction score tracking
PDF report generation via ReportLab
Data processing with Pandas and NumPy
Powered by the Kaggle Global AI Jobs dataset



Tech Stack

LayerTechnologyBackendDjango 4.2.17DatabaseSQLite3FrontendHTML5, CSS3DataPandas ≥ 2.2.3, NumPy ≥ 2.1.0PDF ExportReportLab ≥ 4.2.5DeploymentVercel


Project Structure

SCD-Lab-Final-Project/
├── accounts/        # User authentication (login, register)
├── archive/         # Archived data or older modules
├── core/            # Core app — main models, views, logic
├── insights/        # Analytics and insights module
├── jobs/            # Job listings and market data
├── static/css/      # Stylesheets
├── templates/       # HTML templates
├── db.sqlite3       # SQLite database
├── manage.py        # Django management script
└── requirements.txt # Python dependencies


Getting Started

Prerequisites


Python 3.10+
pip


Installation


Clone the repository


bash   git clone https://github.com/HassanShehryar1/SCD-Lab-Final-Project.git
   cd SCD-Lab-Final-Project


Install dependencies


bash   pip install -r requirements.txt


Apply migrations


bash   python manage.py migrate


Run the development server


bash   python manage.py runserver


Open in browser


   http://127.0.0.1:8000/


Usage


Register a new account or log in with existing credentials.
Access the dashboard to explore AI job market analytics.
Browse salary data, market growth trends, and satisfaction scores.
Export insights as a PDF report.



Dataset

This project uses the Kaggle Global AI Jobs dataset for market analysis and visualizations.


Contributors


HassanShehryar1
SameerHassanGoraya



License

This project was developed for academic purposes as part of the SCD Laboratory course.
