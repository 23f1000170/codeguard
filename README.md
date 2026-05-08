# CodeGuard

CodeGuard is a secure Python code execution and error analysis API built with FastAPI. It allows users to submit Python code for execution, captures the output, and if errors occur, uses Google's Gemini AI to identify the specific lines causing the issues.

## Features

- **Safe Code Execution**: Executes Python code in a controlled environment with output redirection.
- **Error Analysis**: Leverages Gemini AI to pinpoint error-causing lines in the code.
- **RESTful API**: Simple POST endpoint for code submission.
- **CORS Enabled**: Supports cross-origin requests for web applications.
- **Heroku Ready**: Includes Procfile for easy deployment on Heroku.

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd codeguard
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

### Running Locally

Start the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### API Endpoint

**POST /code-interpreter**

Submit Python code for execution and analysis.

#### Request Body
```json
{
  "code": "print('Hello, World!')\nfor i in range(3):\n    print(i)"
}
```

#### Response
- **Success** (no errors):
  ```json
  {
    "error": [],
    "result": "Hello, World!\n0\n1\n2\n"
  }
  ```

- **Error with analysis**:
  ```json
  {
    "error": [2, 3],
    "result": "Traceback (most recent call last):\n  File \"<string>\", line 2, in <module>\n    NameError: name 'undefined_var' is not defined\n"
  }
  ```

### Testing the API

You can use tools like curl or Postman to test the endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/code-interpreter" \
     -H "Content-Type: application/json" \
     -d '{"code": "print(1 + 1)"}'
```

## Deployment

### Heroku

1. Install the Heroku CLI and log in.
2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```
3. Set the Gemini API key as an environment variable:
   ```bash
   heroku config:set GEMINI_API_KEY=your_api_key_here
   ```
4. Deploy:
   ```bash
   git push heroku main
   ```

The app will be available at `https://your-app-name.herokuapp.com`.

## Security Considerations

- This application executes arbitrary Python code, which can be dangerous.
- In production, consider implementing additional security measures such as:
  - Code sandboxing (e.g., using Docker containers)
  - Rate limiting
  - Input validation and sanitization
  - User authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
