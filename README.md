# SmartKeja - Smart Property Rental Platform

A modern, modular frontend application for property rental in Kenya.

## Project Structure

```
├── index.html              # Main HTML file
├── css/
│   ├── main.css           # Main stylesheet (variables, base styles)
│   └── components.css     # Component-specific styles
├── js/
│   ├── main.js            # Application entry point
│   ├── utils/
│   │   └── helpers.js     # Utility functions
│   └── components/
│       ├── navigation.js  # Navigation component
│       ├── filters.js     # Filter functionality
│       ├── search.js      # Search functionality
│       ├── property-listings.js  # Property listing management
│       └── booking.js    # Booking system
└── README.md
```

## Features

- **Modular Architecture**: Separated CSS and JavaScript into organized modules
- **Interactive Filters**: Real-time property filtering by location, price, bedrooms, type
- **Search Functionality**: Live search with debouncing
- **View Toggle**: Switch between grid, list, and map views
- **Booking System**: Interactive calendar and time slot selection
- **Form Validation**: Client-side validation for booking forms
- **Responsive Design**: Mobile-friendly layout
- **Smooth Animations**: CSS transitions and animations

## Getting Started

### Option 1: Using Python HTTP Server

```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

Then open `http://localhost:8000` in your browser.

### Option 2: Using Node.js HTTP Server

```bash
npx http-server -p 8000
```

### Option 3: Using VS Code Live Server

Install the "Live Server" extension and click "Go Live" in VS Code.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

**Note**: ES6 modules require a modern browser and a local server (cannot open HTML file directly).

## JavaScript Features

- ES6 Modules for code organization
- Debounced search for performance
- Dynamic property filtering
- URL parameter management
- Form validation
- Image lazy loading
- Smooth scrolling

## CSS Features

- CSS Custom Properties (variables)
- Flexbox and Grid layouts
- Responsive design with media queries
- CSS animations and transitions
- Component-based styling

## Usage

1. Start a local server (see options above)
2. Open the application in your browser
3. Use filters and search to find properties
4. Click "Book Viewing" to schedule a property viewing
5. Toggle between grid/list/map views using the view buttons

## Development

The codebase uses ES6 modules, so all JavaScript files are organized as modules with `import`/`export` statements. This allows for better code organization and maintainability.

