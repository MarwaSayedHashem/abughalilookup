# Email: How to Deploy Customer Lookup System to Your Company Domain

---

**Subject:** Customer Lookup System - Complete Deployment Instructions

**To:** [Customer Name]  
**From:** [Your Name]  
**Date:** [Date]

---

Dear [Customer Name],

I've prepared detailed step-by-step instructions to deploy the Customer Lookup System to your company domain. Follow these instructions carefully, and the system will be live on your domain.

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- ✅ A server/computer with internet access (Windows Server, Linux, or cloud server)
- ✅ Python 3.8 or higher installed
- ✅ Administrator/root access to the server
- ✅ Your company domain name configured
- ✅ Access to your Autoline and SAP API credentials

---

## 🚀 Step-by-Step Deployment Instructions

### STEP 1: Transfer Files to Your Server

1. **Copy the entire project folder** to your server
   - Location: `C:\CustomerLookup\` (Windows) or `/var/www/customerlookup/` (Linux)
   - Ensure all files are copied, including:
     - `config.json`
     - `manage.py`
     - `customer_lookup/` folder
     - `lookup/` folder
     - `templates/` folder
     - `static/` folder
     - `requirements.txt`

---

### STEP 2: Install Python (if not already installed)

**For Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Verify installation: Open Command Prompt and type `python --version` (should show Python 3.8+)

**For Linux:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

---

### STEP 3: Install Project Dependencies

1. **Open Command Prompt (Windows) or Terminal (Linux)**

2. **Navigate to the project folder:**
   ```bash
   cd C:\CustomerLookup
   ```
   (Replace with your actual project path)

3. **Install all required packages:**
   ```bash
   pip install -r requirements.txt
   ```
   
   If you get permission errors, use:
   ```bash
   pip install --user -r requirements.txt
   ```

4. **Wait for installation to complete** (may take 2-5 minutes)

---

### STEP 4: Configure the Application

1. **Open `config.json` file** with Notepad (Windows) or any text editor

2. **Update Autoline API settings:**
   ```json
   "autoline": {
       "base_url": "http://YOUR_AUTOLINE_SERVER:PORT",
       "token": "YOUR_AUTOLINE_TOKEN"
   }
   ```
   - Replace `YOUR_AUTOLINE_SERVER:PORT` with your actual Autoline server address
   - Replace `YOUR_AUTOLINE_TOKEN` with your actual Autoline API token

3. **Update SAP API settings:**
   ```json
   "sap": {
       "search_base_url": "https://YOUR_SAP_SERVER/sap/opu/odata/sap/ZSD_SP_SEARCH_CUSTOMER_SRV",
       "create_base_url": "https://YOUR_SAP_SERVER/sap/opu/odata/sap/ZAUTOLINE_CUSTOMER_LAKE_CREATE_SRV",
       "search_client": "110",
       "create_client": "110",
       "search_authorization": "Basic YOUR_BASE64_AUTH",
       "create_authorization": "Basic YOUR_BASE64_AUTH",
       "search_cookie": "YOUR_SEARCH_COOKIE",
       "create_cookie": "YOUR_CREATE_COOKIE"
   }
   ```
   - Replace all `YOUR_*` placeholders with your actual SAP credentials
   - See "How to Get SAP Cookies" section below

4. **Update application name (optional):**
   ```json
   "app": {
       "name": "Your Company Customer Lookup",
       "company": "Your Company Name"
   }
   ```

5. **Save the file** (Ctrl+S)

---

### STEP 5: Configure Django Settings

1. **Open `customer_lookup/settings.py`** with a text editor

2. **Find this line:**
   ```python
   ALLOWED_HOSTS = ['*']
   ```

3. **Replace with your domain:**
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```
   (Replace `yourdomain.com` with your actual domain)

4. **For production, change:**
   ```python
   DEBUG = False
   ```

5. **Save the file**

---

### STEP 6: Prepare Static Files

1. **In Command Prompt/Terminal, run:**
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Wait for completion** - this collects all CSS and JavaScript files

---

### STEP 7: Test the Application Locally

1. **Start the server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Open a web browser** and go to:
   ```
   http://localhost:8000
   ```

3. **Test the application:**
   - Enter a Customer MK
   - Click Search
   - Verify it works correctly

4. **If everything works, press Ctrl+C** to stop the server

---

### STEP 8: Set Up for Production (Choose One Option)

#### OPTION A: Using Django's Built-in Server (Simple, for Testing)

1. **Create a batch file (Windows) or script (Linux):**

   **Windows - Create `start_server.bat`:**
   ```batch
   @echo off
   cd /d C:\CustomerLookup
   python manage.py runserver 0.0.0.0:8000
   pause
   ```

   **Linux - Create `start_server.sh`:**
   ```bash
   #!/bin/bash
   cd /var/www/customerlookup
   python3 manage.py runserver 0.0.0.0:8000
   ```

2. **Run the batch file/script** to start the server

3. **Access via:** `http://YOUR_SERVER_IP:8000`

---

#### OPTION B: Using Gunicorn (Recommended for Production)

1. **Install Gunicorn:**
   ```bash
   pip install gunicorn
   ```

2. **Start the server:**
   ```bash
   gunicorn customer_lookup.wsgi:application --bind 0.0.0.0:8000
   ```

3. **For Windows, install Waitress instead:**
   ```bash
   pip install waitress
   waitress-serve --port=8000 customer_lookup.wsgi:application
   ```

---

#### OPTION C: Using Apache/Nginx (Professional Setup)

**See detailed instructions in `DEPLOYMENT_GUIDE.md` file**

---

### STEP 9: Configure Your Domain

1. **Point your domain to your server:**
   - In your domain registrar's control panel
   - Add an A record pointing to your server's IP address
   - Example: `customerlookup.yourdomain.com` → `192.168.1.100`

2. **If using a web server (Apache/Nginx):**
   - Configure virtual host to point to port 8000
   - Set up SSL certificate for HTTPS (recommended)

---

### STEP 10: Set Up Auto-Start (Optional)

**Windows - Create a Windows Service:**
1. Install NSSM (Non-Sucking Service Manager)
2. Create service pointing to your start script
3. Set to start automatically on boot

**Linux - Create a Systemd Service:**
1. Create `/etc/systemd/system/customerlookup.service`
2. Configure to start on boot
3. Enable with: `sudo systemctl enable customerlookup`

---

## 🔑 How to Get SAP Cookies

### For Search API Cookie:

1. Open **Postman** application
2. Make a successful request to your SAP Search API
3. Go to the **Cookies** tab in Postman
4. Find the cookie named `SAP_SESSIONID_PS4_100` (or similar)
5. **Copy the entire cookie value**
6. Paste it in `config.json` → `sap` → `search_cookie`

### For Create API Cookie:

1. Open **Postman**
2. Make a successful request to your SAP Create API
3. In the **Headers** tab, find the `Cookie` header
4. **Copy the entire Cookie header value** (all cookies separated by semicolons)
5. Paste it in `config.json` → `sap` → `create_cookie`

**Note:** Cookies expire periodically. When you get 403 errors, update the cookies in `config.json` and restart the server.

---

## 🔄 How to Update Configuration Later

1. **Edit `config.json`** file
2. **Save the file**
3. **Restart the server** (stop and start again)
4. **No code changes needed!**

---

## 🆘 Troubleshooting

### Problem: "Module not found" errors
**Solution:** Run `pip install -r requirements.txt` again

### Problem: "Port 8000 already in use"
**Solution:** 
- Change port: `python manage.py runserver 0.0.0.0:8001`
- Or stop the other application using port 8000

### Problem: "Static files not loading"
**Solution:** Run `python manage.py collectstatic --noinput` again

### Problem: "API calls failing"
**Solution:**
- Check `config.json` has correct URLs and credentials
- Verify network connectivity to API servers
- Check if cookies have expired (update them)

### Problem: "Can't access from other computers"
**Solution:**
- Ensure firewall allows port 8000
- Use `0.0.0.0:8000` instead of `127.0.0.1:8000`
- Check server's IP address is correct

---

## 📞 Support

If you encounter any issues:

1. **Check the server logs** - they show detailed error messages
2. **Verify `config.json`** - ensure all fields are filled correctly
3. **Test API connectivity** - try the APIs in Postman first
4. **Contact support** with:
   - Error messages from logs
   - Screenshot of the issue
   - Your `config.json` file (remove sensitive tokens before sharing)

---

## 📝 Quick Reference Commands

```bash
# Start server (development)
python manage.py runserver 0.0.0.0:8000

# Start server (production with Gunicorn)
gunicorn customer_lookup.wsgi:application --bind 0.0.0.0:8000

# Collect static files
python manage.py collectstatic --noinput

# Check if Python is installed
python --version

# Install dependencies
pip install -r requirements.txt
```

---

## ✅ Final Checklist

Before going live, verify:
- [ ] All dependencies installed
- [ ] `config.json` configured with correct credentials
- [ ] `ALLOWED_HOSTS` set to your domain
- [ ] Static files collected
- [ ] Server starts without errors
- [ ] Application accessible in browser
- [ ] API calls working (test search functionality)
- [ ] Domain pointing to server (if using domain)
- [ ] Firewall configured (if needed)

---

## 🎉 You're Done!

Once all steps are completed, your Customer Lookup System will be live and accessible at:
- `http://yourdomain.com:8000` (if using direct access)
- `http://yourdomain.com` (if using web server)

**Remember:** After any changes to `config.json`, always restart the server!

---

Best regards,  
[Your Name]  
[Your Contact Information]

---

**Attachments:**
- `DEPLOYMENT_GUIDE.md` - Advanced deployment options
- `CONFIGURATION_GUIDE.md` - Detailed configuration instructions
- `config.json.example` - Configuration template


