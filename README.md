
# Codeflix Catalog API

A **Catalog API** for a video platform built with **FastAPI** and **GraphQL**, powered by **ElasticSearch** for efficient searching and indexing.
This project integrates with **Kafka** and **Kafka Connect** for data streaming, uses **MySQL** as the source of truth, and leverages **Keycloak** for secure authentication and authorization.

## 🚀 Technologies

* **FastAPI** – High-performance API framework
* **GraphQL** – Flexible query and data retrieval
* **ElasticSearch** – Full-text search and indexing
* **Kafka & Kafka Connect** – Event streaming and data pipelines
* **MySQL** – Relational database for persistence
* **Keycloak** – Identity and access management
* **Docker & Docker Compose** – Containerized services for local and production environments

## 📂 Project Overview

The Catalog API is a **core service** in the Codeflix ecosystem.
It:

* Exposes a **GraphQL API** for querying video catalog data.
* Uses **Kafka Connect + Debezium** to synchronize data between MySQL and ElasticSearch.
* Provides **high-performance search capabilities** with ElasticSearch.
* Ensures **secure access** through Keycloak integration.
* Follows modern **microservices and clean architecture principles**.

## ⚙️ Setup & Running

### 1. Clone the repository

```bash
git clone https://github.com/your-username/codeflix-catalog-api.git
cd codeflix-catalog-api
```

### 2. Start all services with Docker Compose

```bash
docker-compose up -d --build
```

This will spin up:

* **MySQL** (database)
* **Kafka** (broker)
* **Kafka Connect** (Debezium pipeline)
* **ElasticSearch** (search engine)
* **FastAPI service** (GraphQL API)
* **Consumer service** (Kafka consumer for ElasticSearch indexing)

### 3. Access the services

* **FastAPI API** → [http://localhost:8000](http://localhost:8000)
* **FastAPI Docs (Swagger UI)** → [http://localhost:8000/docs](http://localhost:8000/docs)
* **GraphQL Playground** → [http://localhost:8000/graphql](http://localhost:8000/graphql)
* **ElasticSearch** → [http://localhost:9200](http://localhost:9200)
* **Kafka Connect** → [http://localhost:8083](http://localhost:8083)
* **MySQL** → `localhost:3306` (user: `codeflix`, password: `codeflix`)

### 4. Running Tests

```bash
docker-compose --profile test up --build
```

This spins up a **test environment** with a dedicated ElasticSearch instance and runs the test suite with **pytest**.

## 📖 Notes

* Data flows from **MySQL → Kafka Connect (Debezium) → Kafka → ElasticSearch**.
* The **FastAPI + GraphQL API** serves data from **ElasticSearch**, ensuring fast queries.
* Authentication is handled via **Keycloak** (not included in the docker-compose file, but required for production).