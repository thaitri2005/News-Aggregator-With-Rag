# **RAG-based AI News Aggregator**

## **Project Overview**

This project is a Retrieval-Augmented Generation (RAG) based AI News Aggregator that scrapes news articles from various sources, provides an interface for users to search for news, and uses AI (via the Google Gemini API) to generate article summaries. The application consists of a React frontend and a Flask backend, with MongoDB used as the database and Docker for containerization.

## **Features**

- **News Aggregation**: Crawl and retrieve news articles from multiple sources.
- **AI-powered Summarization**: Generate concise summaries for articles using the Google Gemini API.
- **Search Functionality**: Users can search for news articles and retrieve relevant results.
- **Responsive UI**: Built with Material-UI (MUI) for a modern and responsive user interface.
- **Containerized Setup**: Easy to deploy with Docker and Docker Compose.

---

## **Prerequisites**

Before you begin, ensure you have the following installed:

- **Docker**: Install Docker
- **Docker Compose**: Install Docker Compose
- **Node.js & npm**: Install Node.js (for local development)

---

## **Setup and Installation**

1. **Clone the Repository**

    ```bash
    git clone https://github.com/thaitri2005/News-Aggregator-With-Rag.git
    cd News-Aggregator-With-Rag
    ```

2. **Set Up Environment Variables**
    Create a `.env` file in the root directory and add the following environment variables:

    ```env
    # MongoDB connection string
    MONGO_URI=your_mongo_db_connection_string

    # Google Gemini API Key
    GEMINI_API_KEY=your_gemini_api_key
    ```

3. **Build and Run the Containers**
    To run the project using Docker, follow these steps:

    **Step 1: Build and Start Containers**

    ```bash
    cd deployment
    docker-compose up --build
    ```

    This command will:
    - Build the backend service (Flask API)
    - Build the frontend service (React app)
    - Build the scheduler service (for scheduling scrapers)
    - Start all services in the app-network

    **Step 2: Access the Application**
    - Frontend: Visit [http://localhost:3000](http://localhost:3000) in your browser.
    - Backend: The Flask API will be running at [http://localhost:5000](http://localhost:5000).

---

## **Available Endpoints (Backend)**

### **GET /articles**

- **Description**: Retrieves a list of all articles in the database.
- **Response**:
  - 200 OK: Returns a list of articles with `_id`, `title`, `content`, `date`, `source_url`, and `source`.
  - 500 Internal Server Error: If something goes wrong during the fetch process.

### **GET /articles/_id**

- **Description**: Fetches a specific article by its ID.
- **Parameters**: `id` (path parameter) – MongoDB ObjectID of the article.
- **Response**:
  - 200 OK: Returns the article corresponding to the given ID.
  - 400 Bad Request: Invalid article ID format.
  - 404 Not Found: Article with the given ID not found.
  - 500 Internal Server Error: If something goes wrong.

### **POST /articles**

- **Description**: Adds a new article to the database.
- **Request Body** (JSON):

    ```json
    {
        "title": "Article Title",
        "content": "Full content of the article",
        "date": "2024-01-01T00:00:00Z",
        "source_url": "https://example.com"
    }
    ```

- **Response**:
  - 201 Created: Article added successfully.
  - 400 Bad Request: Invalid or missing input data.
  - 500 Internal Server Error: If something goes wrong during insertion.

### **GET /summaries**

- **Description**: Fetches all available article summaries in the database.
- **Response**:
  - 200 OK: Returns a list of summaries.
  - 500 Internal Server Error: If something goes wrong during the fetch process.

### **POST /summarize**

- **Description**: Generates a summary for a specific article. If the summary already exists in the database, it will return the stored summary.
- **Request Body** (JSON):

    ```json
    {
        "article_id": "60e4d5f5e8a4e6b450d2f0b5"
    }
    ```

- **Response**:
  - 200 OK: Returns the summary of the article.
  - 400 Bad Request: Missing or invalid article ID.
  - 404 Not Found: Article not found.
  - 500 Internal Server Error: If something goes wrong during summarization or while saving the summary.

### **GET /queries**

- **Description**: Retrieves all saved queries.
- **Response**:
  - 200 OK: Returns a list of queries.
  - 500 Internal Server Error: If something goes wrong during the fetch process.

### **POST /queries**

- **Description**: Adds a new query to the database.
- **Request Body** (JSON):

    ```json
    {
        "query": "Search term",
        "response": "Query response"
    }
    ```

- **Response**:
  - 201 Created: Query added successfully.
  - 400 Bad Request: Invalid or missing input data.
  - 500 Internal Server Error: If something goes wrong during insertion.

### **POST /retrieve**

- **Description**: Retrieves articles that match a search query using MongoDB's text search.
- **Request Body** (JSON):

    ```json
    {
        "query": "Search term",
        "page": 1,
        "limit": 5,
        "sort_by": "score",
        "order": "desc"
    }
    ```

  - `query`: The search term (required).
  - `page`: The page number for pagination (default is 1).
  - `limit`: The number of articles to return per page (default is 5).
  - `sort_by`: Sorting criteria, either "score" (relevance) or "date" (default is "score").
  - `order`: Sorting order, either "asc" or "desc" (default is "desc").
- **Response**:
  - 200 OK: Returns a list of articles matching the search query.
  - 400 Bad Request: Invalid or missing input data.
  - 404 Not Found: No articles found matching the query.
  - 500 Internal Server Error: If something goes wrong during the retrieval process.

### **Error Handlers**

- **400 Bad Request**: Returns a JSON error response when the input is invalid.
- **404 Not Found**: Returns a JSON error response when the requested resource is not found.
- **500 Internal Server Error**: Returns a JSON error response when there’s an internal server issue.

---

## **Technologies Used**

- **Frontend**:
  - React
  - Material-UI (MUI) for design and layout
  - Axios for making HTTP requests to the backend
  - React Props for data handling and passing between components
- **Backend**:
  - Flask (Python)
  - MongoDB (Atlas) for data storage
  - Marshmallow for input validation
- **AI Integration**: Google Gemini API for summarizing articles
- **Containerization**: Docker, Docker Compose for deployment
- **Scheduling**: Python-based scheduler for crawling articles

---

## **Known Issues**

- Ensure your MongoDB Atlas connection string is correct in the `.env` file.
- If the frontend doesn't reload properly, you may need to set `CHOKIDAR_USEPOLLING=true` in the `docker-compose.yml` file for live reloading in Docker.

---

## **Contributing**

Contributions are welcome! If you'd like to contribute, please:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a Pull Request.

---

## **License**

This project is licensed under the MIT License. See the LICENSE file for details.

---

## **Contact**

For any questions or feedback, feel free to reach out to the project owner at <thaihuutri.work@gmail.com>.
