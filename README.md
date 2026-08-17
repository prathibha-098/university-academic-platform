# University Academic Management and Student Success Platform

A full-stack educational management prototype for the Git & Docker Technical Assignment.

## Stack

- Frontend: HTML, CSS, JavaScript + Nginx
- Backend: Python Flask REST API
- Database: PostgreSQL
- Containerization: Docker + Docker Compose
- Version control: Git + GitHub

## Features

- Academic dashboard
- Student records
- Add/delete students
- Attendance and marks tracking
- Academically at-risk student identification
- PostgreSQL persistence
- Separate frontend, backend and database containers

## Run with Docker

From the project root:

```bash
docker compose up --build
```

Open:

- Frontend: http://localhost:8080
- Backend health: http://localhost:5000/api/health
- Student API: http://localhost:5000/api/students
- At-risk API: http://localhost:5000/api/risk

Stop:

```bash
docker compose down
```

## Git workflow

Recommended branches:

```text
main
└── development
    ├── feature-student-management
    ├── feature-dashboard
    └── feature-risk-detection
```
