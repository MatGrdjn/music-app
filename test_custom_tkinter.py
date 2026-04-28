import customtkinter as ctk

app = ctk.CTk()

def button_callback():
    print("Bouton pressé")

app.title("Mon app")
app.geometry("400x150")

button = ctk.CTkButton(
    app, 
    text="Mon bouton", 
    command=button_callback)

button.grid(
    row=0, 
    column=0, 
    padx=0, 
    pady=0)


app.mainloop()