from ui.main_window import App
import load_data

if __name__ == "__main__":
    load_data.demo_seed()
    # load_data.manual_seed()

    app = App()
    app.mainloop()
