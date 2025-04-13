# Virtual Study Room Platform

A Django-based virtual study room platform where students can join group study sessions, share resources, and collaborate in real-time. The platform supports video calls, screen sharing, and document collaboration.

## Features

- Real-time video conferencing using Agora SDK
- Screen sharing capabilities
- Public and private study rooms
- Resource sharing (documents, links, images)
- Real-time chat
- User authentication and authorization
- Responsive design

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A free Agora.io account for video functionality

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd virtual-study-room
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following content:
```
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
AGORA_APP_ID=your-agora-app-id
AGORA_APP_CERTIFICATE=your-agora-app-certificate
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Setting up Agora

1. Sign up for a free account at [Agora.io](https://www.agora.io)
2. Create a new project in the Agora Console
3. Copy the App ID and App Certificate
4. Add these credentials to your `.env` file

## Usage

1. Register an account or log in
2. Browse available study rooms or create your own
3. Join a room to start studying
4. Use the video controls to manage your camera and microphone
5. Share your screen when needed
6. Share resources with other participants
7. Use the chat feature for text communication

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Agora.io](https://www.agora.io)
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/) #   S t u d y S y n c  
 