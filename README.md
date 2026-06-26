# AI Job Market Analytics Dashboard

A Django-based web application that provides real-time insights into the global AI and tech job market — including salary trends, market growth, and job satisfaction scores. Built as the final project for the Software Construction and Development (SCD) laboratory course.


---

## Features

- User authentication (register, login, logout)
- Interactive dashboard with AI/tech job market analytics
- Salary insights and market growth visualizations
- Job satisfaction score tracking
- PDF report generation via ReportLab
- Data processing with Pandas and NumPy
- Powered by the Kaggle Global AI Jobs dataset

---

## Tech Stack

| Layer       | Technology              |
|-------------|-------------------------|
| Backend     | Django 4.2.17           |
| Database    | SQLite3                 |
| Frontend    | HTML5, CSS3             |
| Data        | Pandas ≥ 2.2.3, NumPy ≥ 2.1.0 |
| PDF Export  | ReportLab ≥ 4.2.5       |
| Deployment  | Vercel                  |

---

## Project Structure

```
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
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HassanShehryar1/SCD-Lab-Final-Project.git
   cd SCD-Lab-Final-Project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

4. **Run the development server**
   ```bash
   python manage.py runserver
   ```

5. **Open in browser**
   ```
   http://127.0.0.1:8000/
   ```

---

## Usage

1. Register a new account or log in with existing credentials.
2. Access the dashboard to explore AI job market analytics.
3. Browse salary data, market growth trends, and satisfaction scores.
4. Export insights as a PDF report.

---

## Dataset

This project uses the **Kaggle Global AI Jobs** dataset for market analysis and visualizations.

---

## Contributors

- [HassanShehryar1](https://github.com/HassanShehryar1)
- [SameerHassanGoraya](https://github.com/SameerHassanGoraya)

---

## License

This project was developed for academic purposes as part of the SCD Laboratory course.
