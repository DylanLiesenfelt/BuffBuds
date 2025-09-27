from app import create_app

# look in config.py for configuration options --> app.config.ClassName to change
app = create_app('app.config.DevelopmentConfig')

if __name__ == "__main__":
    app.run() # debug parameter is set by config setting above
