# SmartKeja React Frontend

Professional React frontend for SmartKeja built with Vite, React Router, and modern UI components.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The React app will run on `http://localhost:3000` and proxy API requests to Django at `http://127.0.0.1:8000`

### 3. Build for Production

```bash
npm run build
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable React components
│   │   └── Navbar.jsx
│   ├── pages/          # Page components
│   │   ├── Home.jsx
│   │   ├── Search.jsx
│   │   ├── Signup.jsx
│   │   ├── Login.jsx
│   │   └── Dashboard.jsx
│   ├── context/        # React Context providers
│   │   └── AuthContext.jsx
│   ├── styles/         # CSS files
│   │   ├── index.css
│   │   └── App.css
│   ├── App.jsx         # Main app component
│   └── main.jsx        # Entry point
├── index.html
├── vite.config.js
└── package.json
```

## 🎨 Features

- ✅ Modern, professional UI design
- ✅ Responsive design (mobile-friendly)
- ✅ React Router for navigation
- ✅ Authentication context
- ✅ Property search and filtering
- ✅ Beautiful property cards
- ✅ Smooth animations and transitions
- ✅ Lucide React icons

## 🔧 Configuration

### Vite Proxy

The Vite dev server proxies API requests to Django:
- `/api/*` → `http://127.0.0.1:8000/api/*`
- `/accounts/*` → `http://127.0.0.1:8000/accounts/*`
- `/media/*` → `http://127.0.0.1:8000/media/*`

## 📦 Dependencies

- **React 18** - UI library
- **React Router 6** - Routing
- **Axios** - HTTP client
- **Lucide React** - Icons
- **Vite** - Build tool

## 🎯 Next Steps

1. Install dependencies: `npm install`
2. Start Django server: `python manage.py runserver`
3. Start React dev server: `npm run dev`
4. Open `http://localhost:3000`

## 🔗 Integration with Django

The React app communicates with Django through:
- REST API endpoints (`/api/*`)
- Django authentication (`/accounts/*`)
- Media files (`/media/*`)

Make sure Django CORS is configured to allow requests from `http://localhost:3000`

