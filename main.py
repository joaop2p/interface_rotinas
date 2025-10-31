from lib.app.myapp import MyApp
from flet import app, AppView

def main():
    my_app = MyApp()
    app(target=my_app.run, view=AppView.FLET_APP)

if __name__ == "__main__":
    main()