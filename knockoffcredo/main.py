from main import createApp
from main.views import online_users

app = createApp()

if __name__ == "__main__":
    print(online_users)
    app.run(debug=True, host='0.0.0.0')