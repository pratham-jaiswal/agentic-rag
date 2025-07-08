## Setup .env

- Copy the contents ftom `.env.example` to `.env`.
- Replace the value of `REACT_APP_API_URL` with the URL of your backend API.

## Things you should modify

- `public/favicon.ico` defines the favicon of the app.
- `public/logo192.png` defines the 192x192 icon of the app.
- `public/logo512.png` defines the 512x512 icon of the app.
- `public/manifest.json` defines the manifest of the app. Modify the `short_name` and `name` fields to change the name of the app.
- `public/index.html` defines the HTML of the app. Modify the `title` field to change the title of the app, and the `description` field to change the description of the app. `<meta name="description" content="A React App for Agentic RAG" />` and `<title>RAG App</title>`.
- `src/App.js` defines the React app. Modify the `org-name` field to the name you want to display.
- `src/colors.css` defines the colors of the app. Modify the `:root` to change the colors of the app.

## Get Started

- Install the required packages using `npm install`.
- Run the app using `npm start`.