import yfinance as yf
import time
import threading
import tkinter as tk
from tkinter import font, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta

def get_es_price():
    try:
        # Aggiungi un ritardo casuale per evitare limiti di API
        time.sleep(0.5)
        
        es = yf.Ticker("ES=F")  # Ticker per il future ES
        data = es.history(period="1d", interval="1m")
        if not data.empty:
            close_price = round(data["Close"].iloc[-1], 2)
            open_price = round(data["Open"].iloc[0], 2)
            pct_change = round(((close_price - open_price) / open_price) * 100, 2)
            print(f"Prezzo recuperato: {close_price}, Apertura: {open_price}, Variazione: {pct_change}%")
            return close_price, pct_change
        print("Dati vuoti nella risposta API")
        return "N/A", 0.0
    except Exception as e:
        print(f"Errore nel recupero del prezzo: {e}")
        return "Error", 0.0

def get_es_daily_data():
    try:
        # Aggiungi un ritardo casuale per evitare limiti di API
        time.sleep(0.5)
        
        es = yf.Ticker("ES=F")
        # Ottieni dati dell'ultimo giorno con intervallo di 5 minuti
        data = es.history(period="1d", interval="5m")
        
        if data is not None and not data.empty:
            print(f"Dati recuperati: {len(data)} punti")
        else:
            print("Nessun dato recuperato per il grafico")
        
        return data
    except Exception as e:
        print(f"Errore nel recupero dei dati giornalieri: {e}")
        return None

class ESPriceDisplay:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Rimuove bordi e barra del titolo
        self.root.attributes('-topmost', True)  # Mantiene la finestra sempre in primo piano
        self.root.attributes('-alpha', 0.85)  # Rende la finestra semi-trasparente
        
        # Configurazione della finestra
        self.root.configure(bg='black')
        self.root.wm_attributes('-transparentcolor', 'black')  # Rende il nero completamente trasparente
        self.root.geometry("+0+0")  # Posizione iniziale in alto a sinistra
        
        # Frame principale
        self.main_frame = tk.Frame(root, bg="black")
        self.main_frame.pack(padx=2, pady=2)
        
        # Frame orizzontale per label e grafico
        self.horizontal_frame = tk.Frame(self.main_frame, bg="black")
        self.horizontal_frame.pack(fill=tk.X)
        
        # Frame per le etichette di prezzo e variazione (sulla sinistra)
        self.price_frame = tk.Frame(self.horizontal_frame, bg="black")
        self.price_frame.pack(side=tk.LEFT)
        
        # Costante per il colore della taskbar di Windows
        self.TASKBAR_COLOR = "#F1F1F1"  # Un grigio chiaro che si avvicina al colore della taskbar di Windows 10/11

        # Label per il prezzo - Cambio sfondo al colore della taskbar
        self.custom_font = font.Font(family="Arial", size=10, weight="bold")
        self.price_label = tk.Label(
            self.price_frame, 
            text="ES: Loading...", 
            fg="#333333",  # Grigio scuro per il testo
            bg=self.TASKBAR_COLOR,  # Colore della taskbar
            font=self.custom_font,
            padx=5,
            pady=2
        )
        self.price_label.pack(anchor=tk.W)
        
        # Label per la variazione percentuale
        self.pct_label = tk.Label(
            self.price_frame, 
            text="0.00%", 
            fg="#333333",  # Grigio scuro per default
            bg=self.TASKBAR_COLOR,  # Colore della taskbar
            font=font.Font(family="Arial", size=8),
            padx=5
        )
        self.pct_label.pack(anchor=tk.W)
        
        # Frame per il grafico (ora sulla destra)
        self.chart_frame = tk.Frame(self.horizontal_frame, bg="black")
        self.chart_frame.pack(side=tk.RIGHT, pady=5)
        
        # Inizializza il grafico
        self.fig, self.ax = plt.subplots(figsize=(1.75, 0.38), facecolor=self.TASKBAR_COLOR)  # Colore della taskbar
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.config(highlightthickness=0)  # Rimuove il bordo del canvas
        self.canvas_widget.pack()
        
        # Configura l'aspetto del grafico
        self.ax.set_facecolor(self.TASKBAR_COLOR)  # Colore della taskbar
        self.ax.tick_params(axis='x', colors='black', labelsize=6)  # Modificato da 'white' a 'black'
        self.ax.tick_params(axis='y', colors='black', labelsize=6)  # Modificato da 'white' a 'black'
        for spine in self.ax.spines.values():
            spine.set_color('black')  # Modificato da 'white' a 'black'
            spine.set_linewidth(0.5)
        
        # Aggiunta della funzionalità di trascinamento
        self.main_frame.bind("<ButtonPress-1>", self.start_move)
        self.main_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.main_frame.bind("<B1-Motion>", self.on_motion)
        self.price_frame.bind("<ButtonPress-1>", self.start_move)
        self.price_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.price_frame.bind("<B1-Motion>", self.on_motion)
        self.price_label.bind("<ButtonPress-1>", self.start_move)
        self.price_label.bind("<ButtonRelease-1>", self.stop_move)
        self.price_label.bind("<B1-Motion>", self.on_motion)
        self.pct_label.bind("<ButtonPress-1>", self.start_move)
        self.pct_label.bind("<ButtonRelease-1>", self.stop_move)
        self.pct_label.bind("<B1-Motion>", self.on_motion)
        self.canvas_widget.bind("<ButtonPress-1>", self.start_move)
        self.canvas_widget.bind("<ButtonRelease-1>", self.stop_move)
        self.canvas_widget.bind("<B1-Motion>", self.on_motion)
        
        # Menu contestuale al click destro
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="Esci", command=self.exit_app)
        self.main_frame.bind("<Button-3>", self.show_menu)
        self.price_frame.bind("<Button-3>", self.show_menu)
        self.price_label.bind("<Button-3>", self.show_menu)
        self.pct_label.bind("<Button-3>", self.show_menu)
        self.canvas_widget.bind("<Button-3>", self.show_menu)
        
        # Avvio thread per aggiornare il prezzo e il grafico
        self.update_thread = threading.Thread(target=self.update_price, daemon=True)
        self.update_thread.start()
        
        # Posizionamento automatico vicino alla taskbar
        self.position_near_taskbar()
        
        # Assicura che la finestra rimanga sempre in primo piano
        self.ensure_topmost()
    
    def position_near_taskbar(self):
        # Posiziona la finestra nell'angolo in basso a destra
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calcola posizione per essere vicino alla taskbar
        window_width = 196  # Larghezza ridotta del 30% (da 280 a 196)
        window_height = 48  # Altezza mantenuta uguale
        x_position = screen_width - window_width - 10
        y_position = screen_height - window_height - 10
        
        self.root.geometry(f"+{x_position}+{y_position}")
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def stop_move(self, event):
        self.x = None
        self.y = None
    
    def on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)
    
    def exit_app(self):
        self.root.quit()
    
    def update_chart(self, data):
        if data is None or data.empty:
            print("Nessun dato disponibile per aggiornare il grafico")
            return
        
        self.ax.clear()
        
        # Configura l'aspetto del grafico
        self.ax.set_facecolor(self.TASKBAR_COLOR)  # Colore della taskbar
        
        # Nascondi completamente i tick e le label sugli assi
        self.ax.tick_params(axis='x', colors='#333333', labelsize=6, labelbottom=False, bottom=False)
        self.ax.tick_params(axis='y', colors='#333333', labelsize=6, labelleft=False, left=False)
        
        # Nascondi i bordi del grafico
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        
        # Grafico dei prezzi di chiusura
        last_price = data["Close"].iloc[-1]
        first_price = data["Close"].iloc[0]
        color = 'green' if last_price >= first_price else 'red'
        
        # Traccia la linea
        self.ax.plot(data.index, data["Close"], color=color, linewidth=1.5)
        
        # Aggiungi punti per ogni dato (ridotto per non sovraccaricare il grafico)
        step = max(1, len(data) // 10)  # Mostra circa 10 punti sul grafico
        self.ax.plot(data.index[::step], data["Close"].iloc[::step], 'o', color=color, markersize=2)
        
        # Rimuovi il titolo e le etichette degli assi
        self.ax.set_title('')
        self.ax.set_xlabel('')
        self.ax.set_ylabel('')
        
        # Rimuovi griglia
        self.ax.grid(False)
        
        # Aggiorna il canvas
        self.fig.tight_layout(pad=0.0)
        self.canvas.draw_idle()
    
    def update_price(self):
        while True:
            try:
                # Aggiorna il prezzo corrente e la variazione
                price, pct_change = get_es_price()
                self.price_label.config(text=f"ES: {price}")
                
                print(f"Aggiornamento UI: prezzo={price}, variazione={pct_change}%")
                
                # Imposta il colore in base alla variazione
                color = "darkgreen" if pct_change >= 0 else "darkred"  # Colori più scuri per maggiore leggibilità
                sign = "+" if pct_change > 0 else ""
                self.pct_label.config(text=f"{sign}{pct_change}%", fg=color, bg=self.TASKBAR_COLOR)
                
                # Aggiorna il grafico ogni minuto
                data = get_es_daily_data()
                self.update_chart(data)
            except Exception as e:
                print(f"Errore nell'aggiornamento UI: {e}")
            
            # Riduci l'intervallo di aggiornamento a 5 minuti per diminuire le chiamate API
            time.sleep(60 * 5)
    
    def ensure_topmost(self):
        """Assicura che la finestra rimanga sempre in primo piano."""
        self.root.attributes('-topmost', True)
        # Richiama questa funzione ogni 10 secondi
        self.root.after(10 * 1000, self.ensure_topmost)

def main():
    root = tk.Tk()
    app = ESPriceDisplay(root)
    root.mainloop()

if __name__ == "__main__":
    main()