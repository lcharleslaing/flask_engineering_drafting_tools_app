# Engineering/Drafting Tools

A comprehensive desktop application built with Flask and Electron for engineering calculations, drafting tools, and project management.

## Features

- **Flask Backend**: Modular structure with blueprints for easy maintenance
- **Electron Frontend**: Native desktop application experience
- **TailwindCSS + DaisyUI**: Modern, responsive UI components
- **Modular Architecture**: Easy to extend with new features
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Project Structure

```
flask_drafting_desktop_app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── electron/
│   └── main.js           # Electron main process
├── routes/               # Flask blueprints
│   ├── __init__.py
│   ├── main.py          # Main routes
│   ├── drafting.py      # Drafting tools routes
│   ├── engineering.py   # Engineering tools routes
│   └── tools.py         # Utility tools routes
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── drafting/        # Drafting templates
│   ├── engineering/     # Engineering templates
│   └── tools/           # Tools templates
└── static/              # Static assets
    ├── css/
    │   └── style.css    # Custom styles
    └── js/
        └── app.js       # Main JavaScript
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

## Development

### Running the Application

**Option 1: Development mode (recommended)**
```bash
npm run dev
```
This will start both Flask and Electron simultaneously.

**Option 2: Manual start**
```bash
# Terminal 1: Start Flask
npm run flask

# Terminal 2: Start Electron
npm start
```

### Available Scripts

- `npm start` - Start Electron app only
- `npm run dev` - Start both Flask and Electron for development
- `npm run flask` - Start Flask server only
- `npm run build` - Build the application for distribution
- `npm run dist` - Create distribution packages

## Building for Distribution

```bash
npm run build
```

This will create platform-specific installers in the `dist/` directory.

## Development Notes

- The Flask server runs on `http://127.0.0.1:5000`
- Electron automatically loads the Flask app
- Hot reload is available for Flask during development
- The app is structured for easy addition of new features

## Adding New Features

1. **New Routes**: Add to appropriate blueprint in `routes/` directory
2. **New Templates**: Add to `templates/` directory
3. **New Static Files**: Add to `static/` directory
4. **New Blueprints**: Create new file in `routes/` and register in `app.py`

## Architecture

### Flask Backend
- **Blueprints**: Modular route organization
- **Templates**: Jinja2 templating with base template
- **Static Files**: CSS, JavaScript, and assets
- **CORS**: Enabled for Electron integration

### Electron Frontend
- **Main Process**: Handles window creation and Flask server startup
- **Security**: Context isolation and node integration disabled
- **Auto-start**: Automatically starts Flask server when app launches

### UI Framework
- **TailwindCSS**: Utility-first CSS framework
- **DaisyUI**: Component library built on TailwindCSS
- **Responsive**: Mobile-first responsive design
- **Accessibility**: Built-in accessibility features

## License

MIT License - see LICENSE file for details.
