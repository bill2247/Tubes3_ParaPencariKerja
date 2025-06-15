from ui.main_window import App
import load_data

if __name__ == "__main__":
    data_type = "demo"
    if data_type == "demo":
        load_data.demo_seed()
    elif data_type == "manual":
        load_data.manual_seed()
    
    app = App()
    app.mainloop()
