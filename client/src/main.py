__author__ = "RONI YAAKOBI"

from .pages.App import App
from .pages import ALL_PAGES

if __name__ == "__main__":
    app = App(ALL_PAGES)
    app.mainloop()