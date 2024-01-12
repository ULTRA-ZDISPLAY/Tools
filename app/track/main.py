import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
import pyautogui

# Variables globales pour les coordonnées et la couleur du pixel
pixel_x = 791
pixel_y = 383
last_color = None
running = False  # Ajout de la variable running

# Fonction pour récupérer la couleur du pixel à la position spécifiée sur l'écran
def get_pixel_color():
    global pixel_x, pixel_y
    couleur = pyautogui.screenshot().getpixel((pixel_x, pixel_y))
    return couleur

# Fonction pour enregistrer la couleur du pixel dans la base de données
def save_pixel_color():
    global last_color
    heure_actuelle = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    couleur = get_pixel_color()
    couleur_str = ','.join(map(str, couleur))
    
    if couleur != last_color:
        last_color = couleur
        cursor.execute('INSERT INTO couleur_pixel (heure, couleur) VALUES (?, ?)', (heure_actuelle, couleur_str))
        conn.commit()
        update_table()
        
    root.after(2000, save_pixel_color)  # Appel récursif pour enregistrer la couleur toutes les 2 secondes

# Fonction pour démarrer le suivi de la couleur
def start_tracking():
    global running
    if not running:
        running = True
        save_pixel_color()

# Fonction pour arrêter le suivi de la couleur
def stop_tracking():
    global running
    running = False

# Fonction pour mettre à jour le tableau avec les données de la base de données
def update_table():
    cursor.execute('SELECT * FROM couleur_pixel')
    rows = cursor.fetchall()
    tree.delete(*tree.get_children())  # Efface toutes les lignes actuelles du tableau
    for row in rows:
        id = row[0]
        heure = row[1]
        couleur_str = row[2]
        couleur = tuple(map(int, couleur_str.split(',')))
        tree.insert('', 'end', values=(id, heure, ''), tags=(f'color{id}',))
        tree.tag_configure(f'color{id}', background='#%02x%02x%02x' % couleur)

# Fonction pour mettre à jour les coordonnées et la couleur du pixel
def update_pixel_info():
    global pixel_x, pixel_y
    try:
        pixel_x = int(entry_x.get())
        pixel_y = int(entry_y.get())
        couleur = get_pixel_color()
        color_box.config(bg='#%02x%02x%02x' % couleur)
    except ValueError:
        pass

# Fonction pour afficher la position de la souris par rapport à l'écran
def update_mouse_position():
    x, y = pyautogui.position()
    mouse_position.config(text=f"Position de la souris (écran) : X={x}, Y={y}")
    root.after(100, update_mouse_position)  # Appel récursif pour mettre à jour la position de la souris

# Créer la fenêtre principale
root = tk.Tk()
root.title("Suivi de la couleur du pixel sur l'écran")

# Connexion à la base de données SQLite
conn = sqlite3.connect('couleur_pixel.db')
cursor = conn.cursor()

# Création de la table pour enregistrer les couleurs des pixels
cursor.execute('''
    CREATE TABLE IF NOT EXISTS couleur_pixel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        heure TEXT,
        couleur TEXT
    )
''')
conn.commit()

# Champ de saisie pour les coordonnées X du pixel
label_x = tk.Label(root, text="Coordonnée X du pixel :")
label_x.pack()
entry_x = tk.Entry(root)
entry_x.pack()

# Champ de saisie pour les coordonnées Y du pixel
label_y = tk.Label(root, text="Coordonnée Y du pixel :")
label_y.pack()
entry_y = tk.Entry(root)
entry_y.pack()

# Bouton pour mettre à jour les coordonnées
update_button = tk.Button(root, text="Mettre à jour", command=update_pixel_info)
update_button.pack()

# Affichage de la couleur du pixel récupéré
color_box_label = tk.Label(root, text="Couleur du pixel :")
color_box_label.pack()
color_box = tk.Label(root, width=5, height=2, relief="solid")
color_box.pack()

# Affichage de la position actuelle de la souris par rapport à l'écran
mouse_position = tk.Label(root, text="Position de la souris (écran) :")
mouse_position.pack()

# Lancer la fonction pour mettre à jour la position de la souris au démarrage
update_mouse_position()

# Tableau pour afficher les données
tree = ttk.Treeview(root, columns=('ID', 'Heure', 'Couleur'), show='headings')
tree.heading('ID', text='ID')
tree.heading('Heure', text='Heure')
tree.heading('Couleur', text='Couleur')
tree.pack(padx=10, pady=5, fill='both', expand=True)

# Barre de défilement pour le tableau
scrollbar = ttk.Scrollbar(root, orient='vertical', command=tree.yview)
scrollbar.pack(side='right', fill='y')
tree.configure(yscrollcommand=scrollbar.set)

# Boutons pour démarrer et arrêter le suivi de la couleur
start_button = tk.Button(root, text="Démarrer le suivi", command=start_tracking)
start_button.pack(padx=10, pady=5)

stop_button = tk.Button(root, text="Arrêter le suivi", command=stop_tracking)
stop_button.pack(padx=10, pady=5)

# Fonction pour fermer la connexion à la base de données et quitter l'application
def close_app():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_app)  # Gestion de la fermeture de la fenêtre

# Lancer l'application
root.mainloop()
