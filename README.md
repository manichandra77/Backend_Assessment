# Credit Approval System API

This project is a backend system built with Django and Django Rest Framework to manage a credit approval system. It provides a set of RESTful APIs to register customers, check loan eligibility based on a dynamic credit score, and create and view loans. The entire application is containerized using Docker and uses Celery with Redis for asynchronous data ingestion from Excel files.

---

## ✨ Features

- **Customer Registration**: Add new customers and automatically calculate an `approved_limit` based on their salary.
- **Dynamic Credit Scoring**: Check loan eligibility by calculating a credit score based on historical loan data. The score considers factors like past EMIs paid on time, number of loans, and current debt.
- **Loan Creation**: Create new loans for eligible customers.
- **Loan Viewing**: Retrieve details for a specific loan or view all loans associated with a customer.
- **Asynchronous Data Ingestion**: Load initial customer and loan data from Excel files using Celery background workers.
- **Containerized Environment**: Fully containerized with Docker and Docker Compose for easy setup and deployment.

---

## 🛠️ Tech Stack

- **Backend**: Python, Django, Django Rest Framework
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose
- **Asynchronous Tasks**: Celery, Redis
- **Data Handling**: Pandas

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need to have the following software installed on your machine:
- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

### Installation

1.  **Clone the Repository**
    ```sh
    git clone https://github.com/manichandra77/Backend_Assessment
    cd credit_system
    ```

2.  **Place Data Files**
    -   Place the `customer_data.xlsx` and `loan_data.xlsx` files into the root directory of the project (the same folder as `docker-compose.yml`).

3.  **Build and Start the Containers**
    -   Open a terminal in the project root and run the following command. This will build the Docker images and start the Django app, PostgreSQL database, Redis, and Celery worker.
    ```sh
    docker-compose up -d --build
    ```

4.  **Run Database Migrations**
    -   Apply the database migrations to create the necessary tables.
    ```sh
    docker-compose exec app python manage.py migrate
    ```

5.  **Ingest Initial Data**
    -   Run the command to load the customer and loan data from the Excel files into the database.
    ```sh
    docker-compose exec app python manage.py ingest_data
    ```

The application is now running and accessible at `http://localhost:8000`.

---

## 📖 API Endpoints

Here are the details of the available API endpoints.

### 1. Register a New Customer

- **Endpoint**: `POST /api/register/`
- **Description**: Creates a new customer record and calculates their approved credit limit.
- **Request Body**:
  ```json
  {
      "first_name": "John",
      "last_name": "Doe",
      "age": 30,
      "monthly_income": 75000,
      "phone_number": 1234567890
  }
  ```
- **Success Response (201 Created)**:
  ```json
  {
      "customer_id": 101,
      "first_name": "John",
      "last_name": "Doe",
      "age": 30,
      "monthly_salary": 75000,
      "approved_limit": 2700000,
      "phone_number": 1234567890
  }
  ```

### 2. Check Loan Eligibility

- **Endpoint**: `POST /api/check-eligibility/`
- **Description**: Checks if a customer is eligible for a loan based on their credit score and returns the loan details.
- **Request Body**:
  ```json
  {
      "customer_id": 1,
      "loan_amount": 50000,
      "interest_rate": 10.5,
      "tenure": 12
  }
  ```
- **Success Response (200 OK)**:
  ```json
  {
      "customer_id": 1,
      "approval": true,
      "interest_rate": 10.5,
      "corrected_interest_rate": null,
      "tenure": 12,
      "monthly_installment": 4406.84
  }
  ```

### 3. Create a New Loan

- **Endpoint**: `POST /api/create-loan/`
- **Description**: Processes and creates a new loan for an eligible customer.
- **Request Body**:
  ```json
  {
      "customer_id": 1,
      "loan_amount": 50000,
      "interest_rate": 10.5,
      "tenure": 12
  }
  ```
- **Success Response (201 Created)**:
  ```json
  {
      "loan_id": 201,
      "customer_id": 1,
      "loan_approved": true,
      "message": "Loan Approved",
      "monthly_installment": 4406.84
  }
  ```

### 4. View a Specific Loan

- **Endpoint**: `GET /api/view-loan/<loan_id>/`
- **Description**: Retrieves detailed information about a specific loan, including customer details.
- **Success Response (200 OK)**:
  ```json
  {
      "loan_id": 1,
      "customer": {
          "customer_id": 1,
          "first_name": "Aarav",
          "last_name": "Sharma",
          "age": null,
          "monthly_salary": 55000,
          "approved_limit": 2000000,
          "phone_number": 9876543210
      },
      "loan_amount": "100000.00",
      "interest_rate": "12.00",
      "monthly_payment": "8884.88",
      "tenure": 12
  }
  ```

### 5. View All Loans for a Customer

- **Endpoint**: `GET /api/view-loans/<customer_id>/`
- **Description**: Retrieves a list of all loans taken by a specific customer.
- **Success Response (200 OK)**:
  ```json
  [
      {
          "loan_id": 1,
          "loan_amount": "100000.00",
          "interest_rate": "12.00",
          "monthly_payment": "8884.88",
          "repayments_left": 5
      },
      {
          "loan_id": 2,
          "loan_amount": "50000.00",
          "interest_rate": "10.00",
          "monthly_payment": "4395.96",
          "repayments_left": 8
      }
  ]
  ```
