
from client.src.pages.GUI import App
from client.src.pages import ALL_PAGES

if __name__ == "__main__":
    app = App(ALL_PAGES)
    app.mainloop()