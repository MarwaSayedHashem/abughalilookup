# Deployment Guide

This guide will help you deploy the Customer Lookup System to your company domain.

## 📦 Prerequisites

- Python 3.8 or higher
- Web server (Apache/Nginx) or use Django's built-in server for testing
- Domain name configured

## 🚀 Quick Deployment Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Settings

Edit `customer_lookup/settings.py`:

```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']  # Replace with your domain
DEBUG = False  # Set to False in production
```

### 3. Configure API Settings

Edit `config.json` with your API URLs and credentials (see CONFIGURATION_GUIDE.md)

### 4. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 5. Run Migrations (if needed)

```bash
python manage.py migrate
```

### 6. Start the Server

#### For Testing (Development):
```bash
python manage.py runserver 0.0.0.0:8000
```

#### For Production (with Gunicorn):
```bash
pip install gunicorn
gunicorn customer_lookup.wsgi:application --bind 0.0.0.0:8000
```

## 🌐 Using with Apache/Nginx

### Apache Configuration Example

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    
    Alias /static /path/to/your/project/staticfiles
    <Directory /path/to/your/project/staticfiles>
        Require all granted
    </Directory>
    
    WSGIDaemonProcess customer_lookup python-path=/path/to/your/project python-home=/path/to/venv
    WSGIProcessGroup customer_lookup
    WSGIScriptAlias / /path/to/your/project/customer_lookup/wsgi.py
    
    <Directory /path/to/your/project/customer_lookup>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
</VirtualHost>
```

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔒 Security Considerations

1. **Set DEBUG = False** in production
2. **Use HTTPS** - configure SSL certificate
3. **Restrict ALLOWED_HOSTS** to your domain only
4. **Keep config.json secure** - don't commit it to version control
5. **Use environment variables** for sensitive data (optional)

## 📝 Environment Variables (Optional)

For extra security, you can use environment variables instead of config.json:

```bash
export AUTOLINE_TOKEN="your_token"
export SAP_SEARCH_AUTH="Basic ..."
```

Then update `lookup/views.py` to read from environment variables.

## 🔄 Updating Configuration

1. Edit `config.json`
2. Restart the web server
3. No code changes needed!

## 📊 Monitoring

- Check server logs regularly
- Monitor API response times
- Set up error alerts

## 🆘 Troubleshooting

### Static files not loading
- Run `python manage.py collectstatic`
- Check static file paths in settings.py
- Verify web server configuration

### API calls failing
- Check `config.json` settings
- Verify network connectivity
- Check API credentials are valid

### 500 errors
- Check DEBUG = True temporarily to see error details
- Review server logs
- Verify all dependencies are installed


