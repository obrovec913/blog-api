
DATABASE_CONFIG = {
    'host': 'db',
    'port': 5432,
    'user': 'user',
    'password': 'password',
    'dbname': 'blog_db'
}

# Формируем строку подключения к базе данных
DATABASE_URL = f"postgresql+asyncpg://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['dbname']}"


