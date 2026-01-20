# OrderProcessing

[in progress]\
A production-style REST API for user registration, authentication and asynchronous order processing with background workers, event tracking and Prometheus metrics.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
    - [Docker setup](#docker-setup)
- [Database Schema](#database-schema)
- [Architecture Overview](#architecture-overview)
- [Endpoints](#endpoints)
    - [Auth](#auth)
    - [User](#user)
    - [Order](#order)
    - [Debug](#debug)
- [Validation and Errors](#validation-and-errors)
- [Testing](#testing)
- [Postman Collection](#postman-collection)

## Features

- User registration & authentication (JWT)
- Create orders with multiple items
- Asynchronous order processing using **Celery** + **Redis**
- Order lifecycle tracked via **Order Events**
- Order statuses: `pending`, `processing`, `completed`, `failed`, `cancelled`
- Background email sending (Mailgun)
- Prometheus metrics (`/metrics`)
- Database migrations (Alembic)
- Clean domain separation: models, services, tasks, resources

---

## Tech Stack

- Python 3.13
- Flask + Flask-Smorest
- SQLAlchemy + Alembic
- Redis + Celery
- MySQL
- Mailgun
- JWT (flask-jwt-extended)
- Prometheus (metrics)
- Docker

See [requirements.txt](requirements.txt) and [requirements-dev.txt](requirements-dev.txt).

---

## Installation

### Docker setup

---

## Database schema

![](/readme/database_schema.png)

---

## Architecture Overview

---

## Endpoints

### Auth

### User

### Order

### Debug

---

## Validation and Errors

---

## Testing

---

## Postman Collection