#!/usr/bin/env bash
set -o errexit

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Making fresh migrations..."
python manage.py makemigrations --noinput

echo "==> Running database migrations..."
python manage.py migrate --noinput --run-syncdb

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Creating superuser if needed..."
python manage.py shell -c "from accounts.models import User; User.objects.filter(email='devipanchal0013@gmail.com').exists() or User.objects.create_superuser(email='devipanchal0013@gmail.com', password='IAMDEVI@123', user_type='admin', status='verified')" || true

echo "==> Build complete!"

