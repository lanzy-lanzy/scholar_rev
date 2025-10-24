# 🎓 Scholar - Django Scholarship Management System

A comprehensive scholarship management system built with Django, featuring modern UI, profile picture functionality, and role-based access control.

## ✨ Features

### 🔐 Authentication & User Management
- **Multi-role Authentication**: Student, OSAS Staff, Administrator
- **Profile Management**: Complete profile updates with profile picture support
- **Secure Login/Registration**: Custom authentication with proper validation

### 👤 Profile Picture System
- **Upload & Preview**: Real-time image preview before upload
- **Dynamic Display**: Profile pictures appear in sidebar and header navigation
- **Fallback Support**: Automatic fallback to user initials when no image exists
- **Error Handling**: Graceful error handling for failed image loads

### 🎯 Role-Based Dashboards
- **Student Dashboard**: Browse scholarships, track applications, manage profile
- **OSAS Dashboard**: Review applications, manage approval workflows
- **Admin Dashboard**: Full system administration and user management

### 📱 Modern UI/UX
- **Responsive Design**: Mobile-first approach with TailwindCSS
- **Interactive Elements**: Alpine.js for dynamic interactions
- **Professional Styling**: Custom color palette and modern aesthetics
- **Accessible Navigation**: Conditional sidebar and header navigation

### 🔄 Real-time Features
- **HTMX Integration**: Dynamic content loading without page refreshes
- **Live Updates**: Real-time status updates and notifications
- **Progressive Enhancement**: Works with and without JavaScript

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 4.2+
- Pillow (for image handling)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lanzy-lanzy/scholar_.git
   cd scholar_
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install django pillow
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open http://127.0.0.1:8000 in your browser
   - Use the credentials from `TEST_CREDENTIALS.md` for testing

## 📁 Project Structure

```
scholar_/
├── core/                          # Main application
│   ├── migrations/               # Database migrations
│   ├── management/commands/      # Custom Django commands
│   ├── models.py                # Database models
│   ├── views.py                 # View controllers
│   ├── forms.py                 # Form definitions
│   ├── urls.py                  # URL routing
│   └── admin.py                 # Admin interface
├── templates/                    # HTML templates
│   ├── auth/                    # Authentication templates
│   ├── base/                    # Base templates
│   ├── student/                 # Student-specific templates
│   ├── osas/                    # OSAS staff templates
│   └── admin/                   # Admin templates
├── media/                       # User uploads
│   ├── profile_pictures/        # Profile pictures
│   └── applications/            # Application documents
├── scholar_/                    # Django project settings
└── manage.py                    # Django management script
```

## 🎨 Recent Enhancements

### Profile Picture Integration
- ✅ Added profile picture field to UserProfile model
- ✅ Updated forms to handle file uploads
- ✅ Enhanced profile update template with modern styling
- ✅ Integrated profile pictures in sidebar and header navigation
- ✅ Added fallback support and error handling

### UI/UX Improvements
- ✅ Fixed header dropdown functionality
- ✅ Enhanced sidebar visibility logic
- ✅ Improved responsive design
- ✅ Added Alpine.js interactions
- ✅ Custom logout functionality

## 🔧 Technical Stack

- **Backend**: Django 4.2+
- **Frontend**: TailwindCSS + Alpine.js + HTMX
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Image Processing**: Pillow
- **Authentication**: Django built-in with custom enhancements

## 📱 Responsive Design

The application is fully responsive and works seamlessly across:
- 📱 Mobile devices (320px+)
- 📊 Tablets (768px+)
- 💻 Desktops (1024px+)
- 🖥️ Large screens (1280px+)

## 🔒 Security Features

- CSRF protection on all forms
- Secure file upload handling
- Role-based access control
- Input validation and sanitization
- Secure session management

## 🚧 Development Status

- ✅ **Phase 1**: Core authentication and user management
- ✅ **Phase 2**: Profile picture functionality
- ✅ **Phase 3**: UI/UX enhancements
- 🔄 **Phase 4**: Scholarship application workflow (in progress)
- 📋 **Phase 5**: Admin tools and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, email the development team or open an issue in the GitHub repository.

---

**Made with ❤️ for educational scholarship management**