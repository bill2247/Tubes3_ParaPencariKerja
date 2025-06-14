import configparser
import os

def _get_config_path():
    """Mendapatkan path absolut ke file config.ini di root proyek."""
    try:
        # Menavigasi ke atas dari direktori file saat ini (src/core)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(base_dir))
        return os.path.join(project_root, 'config.ini')
    except NameError:
        # Fallback jika __file__ tidak terdefinisi (misalnya, di beberapa interpreter)
        return 'config.ini'

def get_db_config():
    """Membaca konfigurasi database dari file config.ini."""
    config = configparser.ConfigParser()
    config_path = _get_config_path()

    if not os.path.exists(config_path):
        return None  # File konfigurasi tidak ada

    config.read(config_path)
    if 'database' in config:
        return dict(config['database'])
    return None

def save_db_config(user, password, db_name):
    """Menyimpan konfigurasi database ke file config.ini."""
    config = configparser.ConfigParser()
    config['database'] = {
        'host': 'localhost',
        'user': user,
        'password': password,
        'database': db_name
    }
    config_path = _get_config_path()

    with open(config_path, 'w') as configfile:
        config.write(configfile)
    print(f"Konfigurasi database disimpan di: {config_path}")

