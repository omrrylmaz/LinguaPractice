

from tkinter import Tk
from utils import TypingPracticeApp  # utils.py dosyasındaki sınıfı içe aktarıyoruz

if __name__ == "__main__":
    root = Tk()
    app = TypingPracticeApp(root)
    root.mainloop()

    