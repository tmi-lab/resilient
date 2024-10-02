from decouple import config

class EnvironmentConfig():
    def __init__(self):
        self.__config = {
            'BACKEND_URL': config('BACKEND_URL', default='http://127.0.0.1:8000', cast=str),
            'DB_NAME': config('DB_NAME', default='postgres', cast=str),
            'DB_USER': config('DB_USER', default='postgres', cast=str),
            'DB_PASSWORD': config('DB_PASSWORD', default='admin', cast=str),
            'DB_HOST': config('DB_HOST', default='localhost', cast=str),
            'DB_PORT': config('DB_PORT', default='5432', cast=str),
            'NORMAL_FONT': config('PDF_NORMAL_FONT', default='Arial', cast=str),
            'BOLD_FONT': config('PDF_BOLD_FONT', default='Arial-Bold', cast=str),
            'NORMAL_FONT_PATH': config('PDF_NORMAL_FONT_PATH', default='/usr/share/fonts/truetype/msttcorefonts/Arial.ttf', cast=str),
            'BOLD_FONT_PATH': config('PDF_BOLD_FONT_PATH', default='/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf', cast=str),
            'WITHINGS_CLIENT_ID': config('WITHINGS_CLIENT_ID', default='secret-client-id', cast=str),
            'WITHINGS_COSTUMER_SECRET': config('WITHINGS_COSTUMER_SECRET', default='costumer-secret', cast=str),
            'WITHINGS_CALLBACK_URL': config('WITHINGS_CALLBACK_URL', default='https://resilient.ukdri.care/auth/withings-connected/', cast=str)
        }
        self.__config['BACKEND_URL'] = self.sanitize_url( self.__config['BACKEND_URL'])
        return
    
    def get_config(self, key):
        value = self.__config.get(key)
        if value is None:
            raise KeyError(f"Key '{key}' not found in config")
        return value

    def sanitize_url(self, url):
        return url.rstrip('/')
    