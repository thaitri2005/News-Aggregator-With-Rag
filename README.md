# **Vietnamese RAG-based AI News Aggregator**

## **Project Overview**

This project is a Vietnamese Retrieval-Augmented Generation (RAG) based AI News Aggregator that scrapes news articles from various sources, provides an interface for users to search for news, and uses AI (via the Google Gemini API) to generate article summaries. The backend is built based on the MVC structure with Flask, the frontend with React, PineCone is used as the database for Vector-Indexed Search and Retrieval while Docker is used for containerization.

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
    # Pinecone API Key (required)
    PINECONE_API_KEY=your_pinecone_api_key

    # Pinecone Index Name (optional, defaults to 'aggsum')
    # The index will be created automatically if it doesn't exist
    PINECONE_INDEX_NAME=aggsum

    # Pinecone Region (optional, defaults to 'us-east-1')
    # Only needed if creating a new serverless index
    PINECONE_REGION=us-east-1

    # Pinecone Vector Dimension (optional, defaults to 768 for PhoBERT)
    PINECONE_DIMENSION=768

    # Google Gemini API Key (required)
    GEMINI_API_KEY=your_gemini_api_key
    ```

    **Note:** 
    - The new Pinecone SDK automatically determines the host from your API key, so `PINECONE_HOST` is no longer needed.
    - The index will be created automatically on first run if it doesn't exist.
    - Make sure your Pinecone API key has permissions to create indexes (or create the index manually in the Pinecone console).

3. **Build and Run the Containers**
    To run the project using Docker, follow these steps:

    **Step 1: Build and Start Containers**

    ```bash
    cd deployment
    docker-compose up --build
    ```

    This command will:
    - Build and start the backend (Flask API)
    - Build and start the frontend (React app)
    - Start the scheduler service (for crawling articles)
    - Set up the entire application network

    **Step 2: Access the Application**
    - Frontend: Visit [http://localhost:3000](http://localhost:3000) in your browser.
    - Backend: The Flask API will be running at [http://localhost:5000](http://localhost:5000).

---

## **Available Endpoints (Backend)**

### **POST /api/articles**

- **Description**: Adds a new article to Pinecone, vectorizing the title and storing the content as metadata.
- **Request Body** (JSON):

    ```json
    {
        "title": "Article Title",
        "content": "Full content of the article",
        "date": "2024-01-01T00:00:00Z",
        "source_url": "https://example.com",
        "source": "News Source"
    }
    ```

- **Response**:
  - 201 Created: Article added successfully.
  - 400 Bad Request: Invalid or missing input data.
  - 500 Internal Server Error: If something goes wrong during insertion.

### **POST /api/retrieve**

- **Description**: Retrieves articles based on a query and ranks them using Pinecone vectors. Allows pagination and sorting by relevance or date.
- **Request Body** (JSON):

    ```json
    {
        "query": "Search term",
        "page": 1,
        "limit": 5,
        "sort_by": "score",   // or "date"
        "order": "desc"       // or "asc"
    }
    ```

- **Response**:
  - 200 OK: Returns a list of articles matching the query.
  - 400 Bad Request: Invalid or missing input data.
  - 404 Not Found: No articles found matching the query.
  - 500 Internal Server Error: If something goes wrong during the retrieval process.

### **DELETE /api/clear**

- **Description**: Deletes all vectors in the specified namespace or the default namespace in Pinecone.
- **Query Parameters**:
  - `namespace`: The namespace to clear (default is "default").
  
- **Response**:
  - 200 OK: Success message, all vectors in the specified namespace have been deleted.
  - 400 Bad Request: Invalid namespace provided.
  - 500 Internal Server Error: If there’s an issue with clearing the Pinecone database.

### **POST /api/summarize**

- **Description**: Summarizes an article using the **Gemini API**. The article's content must already exist in Pinecone.
- **Request Body** (JSON):

    ```json
    {
        "article_id": "article-id-here"
    }
    ```

- **Response**:
  - 200 OK: Returns the generated summary of the article.
  - 400 Bad Request: Invalid or missing article ID.
  - 404 Not Found: Article not found in the Pinecone database.
  - 500 Internal Server Error: If summarization fails or another error occurs.

---

## **Technologies Used**

- **Backend**:
  - Flask (Python)
  - APScheduler
  - Pinecone (Vector Database for article storage and search)
  - Google Generative AI (Gemini API) for summarization
  - BeautifulSoup (bs4)
  - Python Dotenv
  - Marshmallow
  - lxml
  - Selenium + Webdriver-Manager
  - Feedparser
- **Frontend**:
  - React
  - Material-UI (MUI)
  - Axios
  - React Props
  - Emotion (styled + react)
  - React Content Loader
  - CSS Loader + Style Loader
  - Webpack
  - Lodash
- **Database**:
  - Pinecone (vector database for storing article titles and metadata)
- **Containerization**: Docker, Docker Compose for deployment

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
