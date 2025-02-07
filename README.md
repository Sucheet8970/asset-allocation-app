# 📌 Asset Allocation Web App  
A **Django-based Asset Allocation System** for managing IT assets, tracking inventory, and handling faulty laptop replacements.  

## 🚀 Features  
✅ **User Authentication** – Secure login for authorities.  
✅ **Dynamic Dashboard** – Real-time data on allocations and inventory.  
✅ **Laptop Inventory Management** – Track installation, license, and allocation status.  
✅ **Laptop Allocation** – Assign laptops and send confirmation emails.  
✅ **Faulty Asset Replacement** – Replace defective laptops and update records.  
✅ **MySQL Database Integration** – Reliable data storage and retrieval.  

## 🛠 Tech Stack  
- **Backend:** Django, Python  
- **Frontend:** HTML, CSS, Bootstrap  
- **Database:** MySQL  
- **Version Control:** Git & GitHub  

## 📦 Installation Guide  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/your_username/asset-allocation-app.git
cd asset-allocation-app
```

### 2️⃣ Create & Activate Virtual Environment  
```bash
python -m venv env
source env/bin/activate  # Mac/Linux  
env\Scripts\activate  # Windows  
```

### 3️⃣ Install Dependencies  
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up MySQL Database  
- Open **MySQL Workbench**  
- Create a new database  
- Import `backup.sql` into MySQL  

### 5️⃣ Update `settings.py` with Database Credentials  
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 6️⃣ Apply Migrations  
```bash
python manage.py migrate
```

### 7️⃣ Create a Superuser (Optional)  
```bash
python manage.py createsuperuser
```

### 8️⃣ Run the Server  
```bash
python manage.py runserver
```
📌 Open **http://127.0.0.1:8000/** in your browser. 🎉  

## 🤝 Contributing  
1. Fork the repository  
2. Create a feature branch (`git checkout -b feature-name`)  
3. Commit changes (`git commit -m "Added new feature"`)  
4. Push to GitHub (`git push origin feature-name`)  
5. Open a Pull Request  

## 📜 License  
This project is licensed under the **MIT License**.  
