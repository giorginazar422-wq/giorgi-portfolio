# GIORGI KHUCHUA — Portfolio

Responsive personal portfolio for Giorgi Khuchua, a frontend development and AI student at Caritas Georgia. It presents his background, skills, design concepts and Course 3 AI chatbot project through a static website with an interactive JavaScript chat demo.

> **Current status:** the website and chat demo run in the browser. This repository does not contain a Python backend or connect to an AI model. Connecting the Python project is a future integration step.

## What is included

- Home, About, Skills, Projects and Contact sections, plus a gallery of design concepts.
- Responsive layouts, a mobile navigation menu and CSS animations.
- A chat interface with predefined replies about Python, Caritas Georgia, skills, email and greetings.
- Email links, a copy-email button and an automatically updated footer year.
- AI-generated visual references in a single image atlas. The portrait is a generated design concept; skill percentages are self-reported.

## Technologies

| Technology | Role in this repository |
| --- | --- |
| HTML5 | Page structure, sections, navigation and chat form. |
| CSS3 | Responsive Grid/Flexbox layouts, gradients, animations and image-atlas positioning. Styles are embedded in `index.html`. |
| Vanilla JavaScript | Menu controls, clipboard interaction and keyword-based chat replies. The script is embedded in `index.html`. |
| GitHub Actions + GitHub Pages | Publish the static frontend using the existing workflow. |
| Python | Described as the language of the Caritas chatbot project; its source, dependencies and API are not included here. |

There is no frontend framework, package manager setup or build step required for the current website.

## Repository structure

| Path | Contents |
| --- | --- |
| [`index.html`](index.html) | Complete page, embedded CSS and JavaScript, including the chat demo. |
| [`assets/portfolio-atlas.jpg`](assets/portfolio-atlas.jpg) | Shared image atlas used for the generated design previews. |
| [`.github/workflows/pages.yml`](.github/workflows/pages.yml) | Static-site deployment on pushes to `main`, or manual runs. |
| [`.nojekyll`](.nojekyll) | Empty marker to disable Jekyll processing when publishing without Jekyll. |
| [`README.md`](README.md) | Project overview, demo limitations and backend integration roadmap. |

## Run locally

Download the repository ZIP and extract it, or clone it:

```bash
git clone https://github.com/giorginazar422-wq/giorgi-portfolio.git
cd giorgi-portfolio
```

Open `index.html` in a browser for a quick preview. For local HTTP development, run this from the repository root with Python 3 installed:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8000>. On Windows, use `py -m http.server 8000 --bind 127.0.0.1` if Python is installed through the Python launcher. Stop the server with Ctrl+C.

This command only serves static files for local development; it does not start a Python chatbot. Clipboard copying depends on browser permissions and context; if copying fails, the page displays the email address.

## How the chat demo works

The submit handler in `index.html` trims the input, converts it to lowercase and searches the `answers` array with `find()` and `includes()`. The first matching keyword wins, in the order shown below. If nothing matches, it displays a fixed help message.

| Keyword, in matching order | Example message | Reply topic |
| --- | --- | --- |
| `python` | `Tell me about Python` | Python's role in the course project |
| `caritas` | `What is Caritas?` | Caritas Georgia and Course 3 |
| `skill` | `What are your skills?` | Self-reported skill levels |
| `email` | `What is your email?` | Contact address |
| `hello` | `Hello!` | Greeting |
| `hi` | `Hi!` | Greeting |

For example, `Python skills` matches both `python` and `skill`, but returns the Python reply because it comes first.

- Replies are predefined strings. There is no language model, semantic understanding, learning or conversation memory.
- Matching uses substrings, not whole words. For example, `this` contains `hi` and can trigger the greeting; English keywords are not a multilingual chat system.
- The input field has a 250-character limit, and whitespace-only submissions are ignored. These are browser-side checks.
- Messages stay in the current page DOM. Reloading resets the conversation; there is no database or persistent chat history.
- The chat code sends no network requests and does not transmit messages to a backend or AI provider.
- New bubbles use `textContent`, so typed text is displayed as text rather than interpreted as HTML.

## GitHub Pages deployment

The existing workflow checks out the repository, uploads its root (`path: .`) and deploys it to GitHub Pages. It runs on pushes to `main` and through `workflow_dispatch`; there is no compilation step. In the repository's **Settings → Pages**, use **GitHub Actions** as the publishing source.

After a successful deployment, the default project URL is [https://giorginazar422-wq.github.io/giorgi-portfolio/](https://giorginazar422-wq.github.io/giorgi-portfolio/).

GitHub Pages hosts static files and does not run a Python web server. The frontend can stay on Pages while a separately hosted HTTPS API handles chat requests. See the [GitHub Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).

## Next steps: connect a Python backend

The following is a proposed implementation plan, not functionality already available in this repository. FastAPI with Uvicorn is one concrete option.

1. **Add the Python service.** Bring in the Python chatbot source and wrap it in an API. A possible layout is `backend/app.py` with a FastAPI instance named `app`, plus `backend/requirements.txt` declaring FastAPI, Uvicorn and the chatbot's dependencies. These files do not exist yet. If backend files are added here, first change the Pages workflow to publish a dedicated folder containing only `index.html`, `assets/` and `.nojekyll`, instead of uploading the entire repository.
2. **Define the API contract.** Add `GET /health` and `POST /api/chat` as described below. Validate the message on the server as a string, reject blank input after trimming and enforce a 250-character limit. Return a non-success HTTP status for invalid input or service failures. Connecting Python alone does not add AI; model-backed replies require an explicit model or provider integration.
3. **Configure CORS.** Allow the frontend origin `https://giorginazar422-wq.github.io` (without `/giorgi-portfolio/`) and the development origin `http://127.0.0.1:8000`. Add or replace the production origin if a custom domain is used. With FastAPI's `CORSMiddleware`, allow the required `GET`/`POST` methods and `Content-Type` header; the middleware handles browser `OPTIONS` preflight requests. CORS is not authentication.
4. **Host the API separately.** Choose a Python web-service host with HTTPS, set its working directory to `backend` and install `requirements.txt`. Use the startup commands below after the proposed files exist. Keep any future provider API keys in server environment variables; do not put them in `index.html`, the repository or the Pages artifact. Add request limits before exposing a paid model API publicly.
5. **Connect the existing form.** In the `chat-form` submit handler, replace the `answers.find(...)` reply selection with an asynchronous `fetch()` POST to the backend's absolute `/api/chat` URL. Send JSON `{ "message": msg }` with `Content-Type: application/json`, check `response.ok`, parse JSON and validate that `reply` is a string before calling `bubble(reply, 'bot')`. Use the local API URL during development and the real HTTPS URL in production; `/api/chat` on the Pages domain will not run Python.
6. **Handle request states.** Show a pending state, prevent duplicate submissions, apply a timeout and restore controls after success or failure. Display a useful error for network, CORS, HTTP or invalid-response failures. Keep an explicit demo mode if desired, and show which mode is active. Update the existing demo labels only when the API integration is working; do not silently present canned fallback replies as AI output.
7. **Verify end to end.** Check successful messages, blank and overlong input, non-success responses, malformed JSON and an unavailable API. Test CORS/preflight from both local development and the deployed Pages origin. Confirm in browser developer tools that the form reaches the intended API and that no provider keys are shipped to the browser. Decide separately whether chat history should be stored; the proposed contract below is stateless.

### Proposed API contract

| Endpoint | Request | Successful response |
| --- | --- | --- |
| `GET /health` | No body. | `200` with `{ "status": "ok" }` |
| `POST /api/chat` | JSON `{ "message": "Hello" }` | `200` with JSON `{ "reply": "Hello!" }` |

The reply above is illustrative. No API endpoint is implemented or deployed by this README.

For failed requests, define a consistent JSON error body such as `{"error":"Message must not be blank."}` alongside documented `4xx` validation and `5xx` server-error statuses. FastAPI's default validation response uses a `detail` field; either normalize it to the chosen format or document and handle that format in the frontend.

### Future backend commands

After creating `backend/app.py` and `backend/requirements.txt`, use an activated Python virtual environment and run:

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```

The local chat URL would be `http://127.0.0.1:8001/api/chat`. The frontend remains on port `8000`.

For a host that supplies a `PORT` environment variable, run this from the `backend` directory as its production start command:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port "$PORT"
```

Use the host's documented port configuration if it does not provide `PORT`, and configure HTTPS through the host. Do not use `--reload` for production.

Implementation references: [FastAPI server deployment](https://fastapi.tiangolo.com/deployment/manually/), [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/), [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch), [Python local HTTP server](https://docs.python.org/3/library/http.server.html).

## Contact

Giorgi Khuchua — [khuchuagiorgi568@gmail.com](mailto:khuchuagiorgi568@gmail.com)
