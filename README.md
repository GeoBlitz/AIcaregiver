# AI Care Assistant

This is an AI-powered Streamlit application that provides support for caregivers of individuals with special needs. The application uses a language model to answer questions and provide guidance based on the documents provided in the `docs` folder.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/AI-Care-Assistant.git
    cd AI-Care-Assistant
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS and Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up your environment variables:**
    *   Create a `.env` file in the root of the project.
    *   Add your Gemini API key to the `.env` file:
        ```
        GEMINI_API_KEY="your-api-key"
        ```

## Running the Application

To run the Streamlit application, use the following command:

```bash
streamlit run app.py
```

## Knowledge Base

The `docs` folder contains the following documents that the AI assistant uses as its knowledge base:

*   `caregivers-handbook-nia_0.pdf`
*   `RGPO-Caregiving-Strategies-Handbook-r3-new-logo.pdf`
*   `UNICEF-Caregivers-Guide-Inclusive-Education-2022.pdf`

You can add more text-based documents to this folder to expand the assistant's knowledge.
