# Production: 2 workers, 4 threads (tối ưu cho performance)
# Nếu dùng gói Basic 256MB và RAM usage cao, có thể giảm xuống:
# web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 60 --access-logfile - --error-logfile -
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60 --access-logfile - --error-logfile -
