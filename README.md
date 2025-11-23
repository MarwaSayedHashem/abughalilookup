# SAP–Autoline Customer Lake

A web-based customer lookup system that integrates Autoline and SAP APIs to provide a unified customer data view.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the application:**
   - Copy `config.json.example` to `config.json`
   - Edit `config.json` with your API credentials (see [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md))

3. **Run the server:**
   ```bash
   python manage.py runserver
   ```

4. **Access the application:**
   - Open your browser and go to `http://localhost:8000`

## 📋 Features

- ✅ Search customers by Customer MK (regular or corporate)
- ✅ Automatic SAP customer code lookup
- ✅ Generate SAP customer codes for new customers
- ✅ Drag-and-drop field reordering
- ✅ Modern, responsive UI
- ✅ Easy configuration via `config.json`

## ⚙️ Configuration

**No programming knowledge required!** All API settings can be changed in `config.json`. See [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) for detailed instructions.

## 🌐 Deployment

For production deployment, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## 📁 Project Structure

```
.
├── config.json              # API configuration (edit this!)
├── config.json.example      # Configuration template
├── customer_lookup/         # Django project settings
├── lookup/                  # Main application
│   ├── views.py            # API endpoints
│   └── urls.py             # URL routing
├── templates/               # HTML templates
├── static/                  # CSS and JavaScript
├── CONFIGURATION_GUIDE.md   # How to edit config.json
└── DEPLOYMENT_GUIDE.md      # Production deployment guide
```

## 🔧 Requirements

- Python 3.8+
- Django 4.0+
- See `requirements.txt` for full list

## 📞 Support

For configuration help, see [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md).

## 📝 License

Internal use only - Abou Ghaly Motors
