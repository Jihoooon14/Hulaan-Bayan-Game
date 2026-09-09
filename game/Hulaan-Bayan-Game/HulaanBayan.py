import tkinter as tk
import random
import math
import threading
import os
from pathlib import Path
from tkinter import font as tkfont

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# ============================================================
# HULAAN BAYAN
# A Filipino Word Challenge
# Enhanced from the original GROUP 5 Advanced Hangman project
# Tkinter only - no external Python packages required
# ============================================================

# ------------------------------------------------------------
# GAME DATA
# ------------------------------------------------------------
WORD_DATA = [
    {"word": "adobo", "category": "Pagkaing Pinoy", "hint": "A famous Filipino dish commonly cooked with vinegar, soy sauce, garlic, and spices."},
    {"word": "sinigang", "category": "Pagkaing Pinoy", "hint": "A Filipino soup known for its sour and savory taste."},
    {"word": "lumpia", "category": "Pagkaing Pinoy", "hint": "A Filipino spring roll often served during celebrations."},
    {"word": "bibingka", "category": "Pagkaing Pinoy", "hint": "A traditional rice cake commonly enjoyed during the Christmas season."},
    {"word": "pancit", "category": "Pagkaing Pinoy", "hint": "A noodle dish often served on birthdays and special occasions."},
    {"word": "halo-halo", "category": "Pagkaing Pinoy", "hint": "A colorful Filipino dessert made with crushed ice, milk, and sweet ingredients."},
    {"word": "lechon", "category": "Pagkaing Pinoy", "hint": "A roasted pig dish often served during major Filipino celebrations."},

    {"word": "patintero", "category": "Larong Pinoy", "hint": "A traditional team game where players try to cross guarded lines."},
    {"word": "sungka", "category": "Larong Pinoy", "hint": "A traditional board game played using shells or small stones."},
    {"word": "sipa", "category": "Larong Pinoy", "hint": "A traditional game where players keep an object in the air using their feet."},
    {"word": "piko", "category": "Larong Pinoy", "hint": "The Filipino version of hopscotch."},
    {"word": "tumbang preso", "category": "Larong Pinoy", "hint": "Players throw slippers at a can while one player guards it."},
    {"word": "luksong tinik", "category": "Larong Pinoy", "hint": "A jumping game where players leap over stacked hands and feet."},

    {"word": "sinulog", "category": "Pistang Pilipino", "hint": "A major festival in Cebu honoring the Santo Niño."},
    {"word": "panagbenga", "category": "Pistang Pilipino", "hint": "Baguio City's famous flower festival."},
    {"word": "masskara", "category": "Pistang Pilipino", "hint": "A Bacolod festival known for colorful smiling masks."},
    {"word": "kadayawan", "category": "Pistang Pilipino", "hint": "A Davao festival celebrating culture, harvest, and thanksgiving."},
    {"word": "pahiyas", "category": "Pistang Pilipino", "hint": "A colorful harvest festival celebrated in Lucban, Quezon."},
    {"word": "ati-atihan", "category": "Pistang Pilipino", "hint": "A lively festival in Kalibo, Aklan known for street dancing and drumbeats."},

    {"word": "palawan", "category": "Lugar sa Pilipinas", "hint": "An island province famous for limestone cliffs, lagoons, and clear waters."},
    {"word": "boracay", "category": "Lugar sa Pilipinas", "hint": "A Philippine island famous for its white-sand beaches."},
    {"word": "mayon", "category": "Lugar sa Pilipinas", "hint": "A volcano in Albay famous for its near-perfect cone shape."},
    {"word": "vigan", "category": "Lugar sa Pilipinas", "hint": "A historic city known for preserved Spanish colonial architecture."},
    {"word": "intramuros", "category": "Lugar sa Pilipinas", "hint": "The historic walled city located in Manila."},
    {"word": "banaue", "category": "Lugar sa Pilipinas", "hint": "A place in Ifugao known for its famous rice terraces."},

    {"word": "bayanihan", "category": "Kulturang Pilipino", "hint": "The Filipino spirit of community cooperation and helping one another."},
    {"word": "jeepney", "category": "Kulturang Pilipino", "hint": "A colorful and iconic form of public transportation in the Philippines."},
    {"word": "parol", "category": "Kulturang Pilipino", "hint": "A star-shaped Filipino Christmas lantern."},
    {"word": "tinikling", "category": "Kulturang Pilipino", "hint": "A traditional dance performed between moving bamboo poles."},
    {"word": "barong", "category": "Kulturang Pilipino", "hint": "A traditional formal garment commonly worn by Filipino men."},
    {"word": "mano po", "category": "Kulturang Pilipino", "hint": "A Filipino gesture of respect toward elders."},

    {"word": "rizal", "category": "Mga Bayani", "hint": "A Filipino national hero who wrote Noli Me Tangere and El Filibusterismo."},
    {"word": "bonifacio", "category": "Mga Bayani", "hint": "The Filipino revolutionary who founded the Katipunan."},
    {"word": "mabini", "category": "Mga Bayani", "hint": "A revolutionary thinker remembered as the Sublime Paralytic."},
    {"word": "lapu-lapu", "category": "Mga Bayani", "hint": "The leader of Mactan remembered for resisting Spanish forces."},
]

# ------------------------------------------------------------
# COLORS - Philippine-inspired modern arcade palette
# ------------------------------------------------------------
BG = "#071426"
BG_2 = "#0B1F3A"
PANEL = "#10294A"
PANEL_2 = "#15365D"
PANEL_3 = "#1B4775"
TEXT = "#FFFDF5"
MUTED = "#C2D0DF"
BLUE = "#2455A4"
RED = "#CE1126"
RED_2 = "#FF8993"
GOLD = "#FCD116"
GREEN = "#58D68D"
GREEN_2 = "#88EDAF"
WHITE = "#FFFFFF"
DARK = "#020817"
FONT = "Arial"

# ------------------------------------------------------------
# ROOT
# ------------------------------------------------------------
root = tk.Tk()
root.title("HULAAN BAYAN - A Filipino Word Challenge")
root.geometry("1180x760")
root.minsize(1180, 760)
root.configure(bg=BG)
try:
    game_icon = tk.PhotoImage(file=str(Path(__file__).parent / "assets" / "logo.png"))
    root.iconphoto(True, game_icon)
except (tk.TclError, OSError):
    pass

root.update_idletasks()
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
ww, wh = 1180, 760
root.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}")

# ------------------------------------------------------------
# STATE
# ------------------------------------------------------------
current_word = ""
current_category = ""
current_hint = ""
guessed_letters = set()
wrong_attempts = 0
score = 0
wins = 0
losses = 0
combo = 0
best_combo = 0
level = 1
difficulty = "KATAMTAMAN"
max_attempts = 5
game_finished = False
hint_used = False
sound_enabled = True
music_enabled = False
music_path = Path(__file__).resolve().parent / "assets" / "bayan-theme.wav"
music_var = tk.StringVar(value="MUSIKA: OFF")
current_screen = None
letter_buttons = {}
particles = []
seen_words = set()
result_after_id = None
modal_open = False
category_choice = tk.StringVar(value="Lahat ng Kategorya")

word_var = tk.StringVar(value="")
category_var = tk.StringVar(value="")
message_var = tk.StringVar(value="Piliin ang antas upang magsimula.")
attempt_var = tk.StringVar(value="")
level_var = tk.StringVar(value="ANTAS 1")
combo_var = tk.StringVar(value="SUNOD-SUNOD x0")
guessed_var = tk.StringVar(value="NAHULAAN: WALA")
difficulty_var = tk.StringVar(value="KATAMTAMAN")

hangman_canvas = None
message_label = None
entry = None
guess_button = None
hint_button = None
word_label = None
category_label = None
game_root_frame = None
stats_score_label = None
stats_wins_label = None
stats_losses_label = None
stats_best_label = None
progress_canvas = None
sound_toggle_button = None

# ------------------------------------------------------------
# SOUND
# ------------------------------------------------------------
def _tone(freq, duration):
    if not sound_enabled:
        return
    try:
        if HAS_WINSOUND:
            winsound.Beep(int(freq), int(duration))
        else:
            root.bell()
    except Exception:
        pass

def play_sequence(sequence):
    if not sound_enabled:
        return
    if not HAS_WINSOUND:
        root.bell()  # Tk calls must stay on the UI thread.
        return
    def worker():
        for freq, duration in sequence:
            if not sound_enabled:
                break
            _tone(freq, duration)
    threading.Thread(target=worker, daemon=True).start()

def sound_click():
    play_sequence([(700, 45)])

def sound_correct():
    play_sequence([(650, 60), (850, 70), (1050, 90)])

def sound_wrong():
    play_sequence([(320, 100), (220, 140)])

def sound_victory():
    play_sequence([(523, 80), (659, 80), (784, 90), (1047, 170)])

def sound_game_over():
    play_sequence([(500, 100), (400, 120), (320, 140), (220, 220)])

def sound_hint():
    play_sequence([(520, 70), (660, 70), (780, 100)])

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    if sound_toggle_button:
        sound_toggle_button.config(text="TUNOG: ON" if sound_enabled else "TUNOG: OFF")
    if sound_enabled:
        sound_click()


def set_music(enabled):
    """Loop the bundled WAV asynchronously; effects have a separate toggle."""
    global music_enabled
    if not HAS_WINSOUND:
        music_enabled = False
        music_var.set("MUSIKA: WINDOWS ONLY")
        return
    try:
        if enabled:
            if not music_path.is_file():
                raise OSError("Missing music asset")
            winsound.PlaySound(str(music_path), winsound.SND_FILENAME |
                               winsound.SND_ASYNC | winsound.SND_LOOP |
                               winsound.SND_NODEFAULT)
        else:
            winsound.PlaySound(None, 0)
        music_enabled = enabled
        music_var.set("MUSIKA: ON" if enabled else "MUSIKA: OFF")
    except (RuntimeError, OSError):
        music_enabled = False
        music_var.set("MUSIKA: UNAVAILABLE")


def toggle_music():
    set_music(not music_enabled)


def music_button(parent):
    button = make_button(parent, "", toggle_music, bg_color=PANEL_3,
                         hover="#245E94", width=25)
    button.config(textvariable=music_var)
    if not HAS_WINSOUND:
        button.config(state="disabled")
    return button

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def make_button(parent, text, command, bg_color=PANEL_3, fg_color=TEXT,
                hover=None, width=None, padx=18, pady=10, font_size=10):
    hover_color = hover or PANEL_2
    def wrapped():
        sound_click()
        command()
    btn = tk.Button(
        parent, text=text, command=wrapped,
        bg=bg_color, fg=fg_color,
        activebackground=hover_color, activeforeground=fg_color,
        relief="flat", bd=0, cursor="hand2",
        padx=padx, pady=pady, width=width,
        font=(FONT, font_size, "bold")
    )
    def enter(_):
        if str(btn["state"]) != "disabled":
            btn.config(bg=hover_color)
    def leave(_):
        if str(btn["state"]) != "disabled":
            btn.config(bg=bg_color)
    btn.bind("<Enter>", enter)
    btn.bind("<Leave>", leave)
    return btn

# ------------------------------------------------------------
# BACKGROUND
# ------------------------------------------------------------
background_canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
background_canvas.place(x=0, y=0, relwidth=1, relheight=1)

app = tk.Frame(root, bg=BG)
app.place(x=0, y=0, relwidth=1, relheight=1)

def create_particles():
    background_canvas.delete("all")
    particles.clear()
    width = max(root.winfo_width(), 1100)
    height = max(root.winfo_height(), 700)

    # subtle sun-ray motif
    cx, cy = width * 0.10, height * 0.13
    for deg in range(0, 360, 30):
        r1, r2 = 28, 70
        a = math.radians(deg)
        background_canvas.create_line(
            cx + math.cos(a)*r1, cy + math.sin(a)*r1,
            cx + math.cos(a)*r2, cy + math.sin(a)*r2,
            fill="#213A5A", width=2
        )
    background_canvas.create_oval(cx-20, cy-20, cx+20, cy+20, outline="#2B4668", width=2)

    # fiesta bunting
    x = 0
    while x < width:
        col = random.choice([BLUE, RED, GOLD])
        background_canvas.create_polygon(x, 28, x+20, 28, x+10, 50, fill=col, outline="")
        x += 42

    # moving decorative dots
    for _ in range(45):
        x = random.randint(0, width)
        y = random.randint(60, height)
        r = random.choice([1, 1, 2])
        color = random.choice(["#244A70", "#2B4B67", "#3C4C6C"])
        obj = background_canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
        particles.append({"id": obj, "x": x, "y": y, "speed": random.uniform(0.15, 0.55), "phase": random.uniform(0, 6.2)})

def animate_particles():
    h = max(root.winfo_height(), 700)
    w = max(root.winfo_width(), 1100)
    for p in particles:
        p["y"] += p["speed"]
        p["phase"] += 0.02
        p["x"] += math.sin(p["phase"]) * 0.08
        if p["y"] > h + 10:
            p["y"] = 55
            p["x"] = random.randint(0, w)
        background_canvas.coords(p["id"], p["x"]-1.5, p["y"]-1.5, p["x"]+1.5, p["y"]+1.5)
    root.after(40, animate_particles)

# ------------------------------------------------------------
# SCREEN MANAGER
# ------------------------------------------------------------
def show_screen(name):
    global current_screen, modal_open
    cancel_result()
    modal_open = False
    current_screen = name
    clear_frame(app)
    if name == "menu":
        build_menu()
    elif name == "difficulty":
        build_difficulty_screen()
    elif name == "game":
        build_game_screen()
    elif name == "how":
        build_how_to_play()

# ------------------------------------------------------------
# MENU
# ------------------------------------------------------------
def build_menu():
    wrapper = tk.Frame(app, bg=BG)
    wrapper.pack(fill="both", expand=True)

    tk.Frame(wrapper, bg=BG, height=20).pack()
    try:
        logo = tk.PhotoImage(file=str(Path(__file__).parent / "assets" / "logo.png"))
        logo = logo.subsample(max(1, math.ceil(logo.width() / 96)))
        logo_label = tk.Label(wrapper, image=logo, bg=BG)
        logo_label.image = logo
        logo_label.pack(pady=(0, 6))
    except (tk.TclError, OSError):
        pass

    tk.Label(
        wrapper, text="  SALITANG PINOY CHALLENGE  ",
        bg="#122E53", fg=GOLD,
        font=(FONT, 10, "bold"), padx=12, pady=6
    ).pack(pady=(10, 15))

    tk.Label(
        wrapper, text="HULAAN BAYAN",
        bg=BG, fg=TEXT, font=(FONT, 36, "bold")
    ).pack()

    tk.Label(
        wrapper, text="A FILIPINO WORD CHALLENGE",
        bg=BG, fg=GOLD, font=(FONT, 16, "bold")
    ).pack(pady=(2, 10))

    tk.Label(
        wrapper,
        text="Tuklasin ang salitang Pilipino bago maubos ang iyong pagkakataon!",
        bg=BG, fg=MUTED, font=(FONT, 11)
    ).pack(pady=(0, 16))

    card = tk.Frame(wrapper, bg=PANEL, padx=36, pady=18,
                    highlightthickness=1, highlightbackground="#2D5B8B")
    card.pack()

    tk.Label(card, text="MABUHAY!  HANDA KA NA BA?",
             bg=PANEL, fg=GREEN, font=(FONT, 10, "bold")).pack(pady=(0, 18))

    make_button(card, "SIMULAN ANG LARO", lambda: show_screen("difficulty"),
                bg_color=GOLD, fg_color=DARK, hover="#FFE36E", width=25, pady=12, font_size=11).pack(pady=6)

    make_button(card, "PAANO MAGLARO", lambda: show_screen("how"),
                bg_color=BLUE, hover="#3269C7", width=25).pack(pady=6)

    music_button(card).pack(pady=6)

    make_button(card, "LUMABAS", on_close,
                bg_color="#421D2A", hover="#672B3C", fg_color="#FF8A97", width=25).pack(pady=6)

    tk.Label(
        wrapper,
        text="Isang letra. Buong kultura.  |  6 kategorya  |  3 antas ng hirap",
        bg=BG, fg=MUTED, font=(FONT, 9)
    ).pack(side="bottom", pady=20)

# ------------------------------------------------------------
# HOW TO PLAY
# ------------------------------------------------------------
def build_how_to_play():
    wrapper = tk.Frame(app, bg=BG)
    wrapper.pack(fill="both", expand=True, padx=80, pady=50)

    tk.Label(wrapper, text="PAANO MAGLARO", bg=BG, fg=TEXT,
             font=(FONT, 30, "bold")).pack(anchor="w")
    tk.Label(wrapper, text="HULAAN BAYAN / GABAY NG MANLALARO",
             bg=BG, fg=GOLD, font=(FONT, 11, "bold")).pack(anchor="w", pady=(2, 25))

    card = tk.Frame(wrapper, bg=PANEL, padx=30, pady=24,
                    highlightthickness=1, highlightbackground="#2D5B8B")
    card.pack(fill="both", expand=True)

    rules = [
        ("01", "Hulaan ang salita", "Pumili ng letra gamit ang on-screen keyboard o physical keyboard."),
        ("02", "Ingatan ang pagkakataon", "Bawat maling letra ay bawas sa natitirang pagkakataon."),
        ("03", "Palakihin ang combo", "Sunod-sunod na tamang hula ay nagbibigay ng mas maraming puntos."),
        ("04", "Gamitin ang pahiwatig", "Makakatulong ang hint pero may katumbas itong 5 puntos."),
        ("05", "Umakyat ng antas", "Manalo ng mga round upang makakuha ng mas mahahabang salita."),
        ("06", "Kilalanin ang Pilipinas", "Ang mga salita ay mula sa pagkaing Pinoy, laro, pista, lugar, bayani, at kultura."),
    ]

    for num, title, desc in rules:
        row = tk.Frame(card, bg=PANEL)
        row.pack(fill="x", pady=7)
        tk.Label(row, text=num, bg="#16395E", fg=GOLD,
                 width=4, pady=8, font=(FONT, 9, "bold")).pack(side="left")
        box = tk.Frame(row, bg=PANEL)
        box.pack(side="left", padx=15)
        tk.Label(box, text=title, bg=PANEL, fg=TEXT, font=(FONT, 11, "bold")).pack(anchor="w")
        tk.Label(box, text=desc, bg=PANEL, fg=MUTED, font=(FONT, 9), wraplength=720, justify="left").pack(anchor="w")

    make_button(wrapper, "BALIK", lambda: show_screen("menu"),
                bg_color=PANEL_3, hover="#245E94").pack(anchor="w", pady=(18, 0))

# ------------------------------------------------------------
# DIFFICULTY
# ------------------------------------------------------------
def set_difficulty(mode):
    global difficulty, max_attempts
    difficulty = mode
    max_attempts = {"MADALI": 6, "KATAMTAMAN": 5, "MAHIRAP": 4}[mode]
    difficulty_var.set(mode)
    start_campaign()

def build_difficulty_screen():
    wrapper = tk.Frame(app, bg=BG)
    wrapper.pack(fill="both", expand=True, padx=70, pady=55)

    tk.Label(wrapper, text="PILIIN ANG ANTAS", bg=BG, fg=TEXT,
             font=(FONT, 32, "bold")).pack()
    tk.Label(wrapper, text="Piliin ang hirap ng iyong hamon.",
             bg=BG, fg=MUTED, font=(FONT, 11)).pack(pady=(4, 12))
    tk.Label(wrapper, text="KATEGORYA", bg=BG, fg=GOLD,
             font=(FONT, 9, "bold")).pack()
    categories = ["Lahat ng Kategorya"] + sorted({item["category"] for item in WORD_DATA})
    selector = tk.OptionMenu(wrapper, category_choice, *categories)
    selector.config(bg=PANEL_3, fg=TEXT, activebackground=BLUE,
                    activeforeground=TEXT, highlightthickness=0, width=25)
    selector["menu"].config(bg=PANEL, fg=TEXT)
    selector.pack(pady=(4, 16))

    cards = tk.Frame(wrapper, bg=BG)
    cards.pack()

    options = [
        ("MADALI", "6 PAGKAKATAON", "Para sa nagsisimula", GREEN, "#123A2A"),
        ("KATAMTAMAN", "5 PAGKAKATAON", "Balanseng hamon", GOLD, "#3C3310"),
        ("MAHIRAP", "4 PAGKAKATAON", "Para sa bihasang manlalaro", RED_2, "#3C1B24"),
    ]

    for mode, lives, desc, accent, darkbg in options:
        card = tk.Frame(cards, bg=PANEL, width=265, height=300, padx=24, pady=25,
                        highlightthickness=1, highlightbackground="#2D5B8B")
        card.pack(side="left", padx=12)
        card.pack_propagate(False)
        tk.Label(card, text=mode, bg=PANEL, fg=accent, font=(FONT, 19, "bold")).pack(pady=(8, 15))
        tk.Label(card, text=lives, bg=darkbg, fg=accent,
                 font=(FONT, 11, "bold"), padx=15, pady=8).pack(pady=8)
        tk.Label(card, text=desc, bg=PANEL, fg=MUTED, font=(FONT, 10)).pack(pady=(10, 28))
        make_button(card, f"PILIIN: {mode}", lambda m=mode: set_difficulty(m),
                    bg_color=accent, fg_color=DARK if mode != "MAHIRAP" else WHITE,
                    hover=accent, width=18).pack()

    make_button(wrapper, "BALIK SA MENU", lambda: show_screen("menu"),
                bg_color=PANEL_3, hover="#245E94").pack(pady=30)

# ------------------------------------------------------------
# GAME SCREEN
# ------------------------------------------------------------
def build_game_screen():
    global hangman_canvas, message_label, entry, guess_button, hint_button
    global word_label, category_label, game_root_frame
    global stats_score_label, stats_wins_label, stats_losses_label
    global stats_best_label, progress_canvas, letter_buttons, sound_toggle_button

    game_root_frame = tk.Frame(app, bg=BG)
    game_root_frame.pack(fill="both", expand=True, padx=28, pady=22)

    header = tk.Frame(game_root_frame, bg=BG)
    header.pack(fill="x", pady=(0, 14))

    left = tk.Frame(header, bg=BG)
    left.pack(side="left")
    tk.Label(left, text="HULAAN BAYAN", bg=BG, fg=GOLD,
             font=(FONT, 13, "bold")).pack(anchor="w")
    tk.Label(left, text="A Filipino Word Challenge", bg=BG, fg=TEXT,
             font=(FONT, 24, "bold")).pack(anchor="w")
    tk.Label(left, text="Hulaan ang salitang Pilipino at ipakita ang iyong galing!",
             bg=BG, fg=MUTED, font=(FONT, 11)).pack(anchor="w", pady=(2, 0))

    stats = tk.Frame(header, bg=PANEL, padx=14, pady=9)
    stats.pack(side="right")
    stats_score_label = tk.Label(stats, text="PUNTOS 0", bg=PANEL, fg=TEXT, font=(FONT, 13, "bold"))
    stats_score_label.pack(side="left", padx=9)
    stats_wins_label = tk.Label(stats, text="PANALO 0", bg=PANEL, fg=GREEN, font=(FONT, 13, "bold"))
    stats_wins_label.pack(side="left", padx=9)
    stats_losses_label = tk.Label(stats, text="TALO 0", bg=PANEL, fg=RED_2, font=(FONT, 13, "bold"))
    stats_losses_label.pack(side="left", padx=9)

    content = tk.Frame(game_root_frame, bg=BG)
    content.pack(fill="both", expand=True)

    left_panel = tk.Frame(content, bg=PANEL, width=365, padx=18, pady=18,
                          highlightthickness=1, highlightbackground="#2D5B8B")
    left_panel.pack(side="left", fill="y")
    left_panel.pack_propagate(False)

    top_left = tk.Frame(left_panel, bg=PANEL)
    top_left.pack(fill="x")
    tk.Label(top_left, text="KALAGAYAN", bg=PANEL, fg=MUTED,
             font=(FONT, 11, "bold")).pack(side="left")
    tk.Label(top_left, textvariable=difficulty_var, bg="#16395E", fg=GOLD,
             padx=8, pady=4, font=(FONT, 10, "bold")).pack(side="right")

    hangman_canvas = tk.Canvas(left_panel, bg=PANEL, width=325, height=360, highlightthickness=0)
    hangman_canvas.pack(pady=(7, 0))

    tk.Label(left_panel, textvariable=attempt_var, bg=PANEL, fg=GOLD,
             font=(FONT, 16, "bold")).pack(pady=(0, 8))

    progress_canvas = tk.Canvas(left_panel, bg="#213E61", height=12, highlightthickness=0)
    progress_canvas.pack(fill="x", padx=8)
    progress_canvas.bind("<Configure>", lambda event: update_lives())

    small = tk.Frame(left_panel, bg=PANEL)
    small.pack(fill="x", pady=(15, 0))
    for col in range(2):
        small.grid_columnconfigure(col, weight=1)
    tk.Label(small, textvariable=level_var, bg=PANEL_2, fg=GOLD,
             pady=9, font=(FONT, 11, "bold")).grid(row=0, column=0, sticky="ew", padx=(0, 4))
    tk.Label(small, textvariable=combo_var, bg=PANEL_2, fg="#B8D8FF",
             pady=9, font=(FONT, 11, "bold")).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    right_panel = tk.Frame(content, bg=PANEL, padx=18, pady=16,
                           highlightthickness=1, highlightbackground="#2D5B8B")
    right_panel.pack(side="left", fill="both", expand=True, padx=(14, 0))

    tk.Label(right_panel, text="KATEGORYA", bg=PANEL, fg=MUTED,
             font=(FONT, 10, "bold")).pack()
    category_label = tk.Label(right_panel, textvariable=category_var, bg=PANEL,
                              fg=GOLD, font=(FONT, 13, "bold"))
    category_label.pack(pady=(2, 11))

    word_label = tk.Label(right_panel, textvariable=word_var, bg=PANEL,
                          fg=TEXT, font=("Courier New", 25, "bold"))
    word_label.pack(fill="x", pady=(3, 12))
    word_label.bind("<Configure>", lambda event: fit_word())

    message_label = tk.Label(right_panel, textvariable=message_var, bg=PANEL,
                             fg=MUTED, font=(FONT, 13, "bold"))
    message_label.pack(pady=(0, 9))

    tk.Label(right_panel, textvariable=guessed_var, bg=PANEL, fg=MUTED,
             font=(FONT, 10), wraplength=600).pack(pady=(0, 12))

    keyboard_frame = tk.Frame(right_panel, bg=PANEL)
    keyboard_frame.pack(pady=(4, 8))

    letter_buttons = {}
    for row_text in ["ABCDEFGHI", "JKLMNOPQR", "STUVWXYZ"]:
        row_frame = tk.Frame(keyboard_frame, bg=PANEL)
        row_frame.pack(pady=3)
        for letter in row_text:
            btn = tk.Button(
                row_frame, text=letter, width=3, height=1,
                bg=PANEL_3, fg=TEXT,
                activebackground=GOLD, activeforeground=DARK,
                relief="flat", bd=0, cursor="hand2",
                font=(FONT, 11, "bold"),
                command=lambda l=letter.lower(): (sound_click(), guess_letter(l))
            )
            btn.config(font=(FONT, 14, "bold"), disabledforeground=TEXT)
            btn.pack(side="left", padx=3, ipady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#245E94") if str(b["state"]) != "disabled" else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=PANEL_3) if str(b["state"]) != "disabled" else None)
            letter_buttons[letter.lower()] = btn

    input_frame = tk.Frame(right_panel, bg=PANEL)
    input_frame.pack(pady=(12, 8))

    tk.Label(input_frame, text="ISANG LETRA", bg=PANEL, fg=MUTED,
             font=(FONT, 10, "bold")).pack(side="left", padx=(0, 12))
    entry = tk.Entry(input_frame, width=7, justify="center", bg=BG_2, fg=TEXT,
                     insertbackground=TEXT, relief="flat", bd=0, font=(FONT, 15, "bold"))
    entry.pack(side="left", ipady=8)
    guess_button = make_button(input_frame, "HULA", guess_from_entry,
                               bg_color=GOLD, fg_color=DARK, hover="#FFE36E", padx=18, pady=8)
    guess_button.pack(side="left", padx=(8, 0))
    entry.bind("<Return>", lambda e: guess_from_entry())

    actions = tk.Frame(right_panel, bg=PANEL)
    actions.pack(pady=(7, 0))

    hint_button = make_button(actions, "PAHIWATIG", show_hint,
                              bg_color=PANEL_3, hover="#245E94", padx=13, pady=8)
    hint_button.pack(side="left", padx=4)
    make_button(actions, "BAGONG SALITA", new_game,
                bg_color=GREEN, fg_color=DARK, hover=GREEN_2, padx=13, pady=8).pack(side="left", padx=4)
    make_button(actions, "MENU", lambda: show_screen("menu"),
                bg_color="#2A3B50", hover="#3B506A", padx=13, pady=8).pack(side="left", padx=4)

    settings = tk.Frame(right_panel, bg=PANEL)
    settings.pack(pady=(14, 0))
    sound_toggle_button = make_button(settings, "TUNOG: ON" if sound_enabled else "TUNOG: OFF",
                                      toggle_sound, bg_color="#24364A", hover="#314A64", padx=13, pady=8)
    sound_toggle_button.pack(side="left", padx=4)
    music_control = music_button(settings)
    music_control.config(width=13, padx=10, pady=8)
    music_control.pack(side="left", padx=4)

    footer = tk.Frame(game_root_frame, bg=BG)
    footer.pack(fill="x", pady=(13, 0))
    tk.Label(footer, text="TAMA +10  •  MALI -5  •  PAHIWATIG -5  •  PANALO +50",
             bg=BG, fg=MUTED, font=(FONT, 10)).pack(side="left")
    stats_best_label = tk.Label(footer, text=f"PINAKAMAHUSAY NA COMBO x{best_combo}",
                                bg=BG, fg="#B8D8FF", font=(FONT, 10, "bold"))
    stats_best_label.pack(side="right")

    update_everything()
    draw_hangman()
    if not current_word:
        new_game()
    else:
        update_word_display()
    root.after(100, lambda: entry.focus_set()
               if current_screen == "game" and entry and entry.winfo_exists() else None)

# ------------------------------------------------------------
# GAME RESET / WORD SELECTION
# ------------------------------------------------------------
def start_campaign():
    global score, wins, losses, combo, best_combo, level
    global current_word, guessed_letters, wrong_attempts, game_finished
    score = wins = losses = combo = best_combo = 0
    level = 1
    current_word = ""
    guessed_letters = set()
    wrong_attempts = 0
    game_finished = False
    seen_words.clear()
    show_screen("game")

def normalized_letters(text):
    return [ch for ch in text.lower() if ch.isalpha()]

def choose_word():
    available = [item for item in WORD_DATA if category_choice.get() == "Lahat ng Kategorya"
                 or item["category"] == category_choice.get()]
    letters_count = lambda item: len(normalized_letters(item["word"]))
    if level <= 2:
        pool = [x for x in available if letters_count(x) <= 7]
    elif level <= 4:
        pool = [x for x in available if 7 <= letters_count(x) <= 10]
    else:
        pool = [x for x in available if letters_count(x) >= 9]
    pool = pool or available
    unseen = [item for item in pool if item["word"] not in seen_words]
    if not unseen:
        seen_words.difference_update(item["word"] for item in pool)
        unseen = [item for item in pool if item["word"] != current_word] or pool
    selected = random.choice(unseen)
    seen_words.add(selected["word"])
    return selected


def cancel_result():
    global result_after_id
    if result_after_id is not None:
        root.after_cancel(result_after_id)
        result_after_id = None


def schedule_result(callback):
    global result_after_id
    cancel_result()
    def show():
        global result_after_id
        result_after_id = None
        if current_screen == "game" and game_finished:
            callback()
    result_after_id = root.after(350, show)

def new_game():
    global current_word, current_category, current_hint
    global guessed_letters, wrong_attempts, game_finished, hint_used, combo

    if current_screen != "game":
        return
    cancel_result()

    selected = choose_word()
    current_word = selected["word"].lower()
    current_category = selected["category"]
    current_hint = selected["hint"]
    guessed_letters = set()
    wrong_attempts = 0
    game_finished = False
    hint_used = False
    combo = 0

    category_var.set(current_category)
    message_var.set("Pumili ng letra at hulaan ang salitang Pilipino.")
    if message_label:
        message_label.config(fg=MUTED)

    if entry:
        entry.config(state="normal")
        entry.delete(0, tk.END)
    if guess_button:
        guess_button.config(state="normal")
    if hint_button:
        hint_button.config(state="normal", text="PAHIWATIG")

    for button in letter_buttons.values():
        button.config(state="normal", bg=PANEL_3, fg=TEXT)

    update_everything()
    draw_hangman()
    if entry:
        entry.focus_set()

# ------------------------------------------------------------
# DISPLAY
# ------------------------------------------------------------
def update_word_display():
    chars = []
    for ch in current_word:
        if ch.isalpha():
            chars.append(ch.upper() if ch in guessed_letters else "_")
        elif ch == " ":
            chars.append(" ")
        else:
            chars.append(ch)
    word_var.set(" ".join(chars))
    fit_word()


def fit_word():
    if not word_label or not word_label.winfo_exists():
        return
    available_width = max(200, word_label.master.winfo_width() - 60)
    for size in range(34, 11, -1):
        if tkfont.Font(family="Courier New", size=size, weight="bold").measure(word_var.get()) <= available_width:
            break
    word_label.config(font=("Courier New", size, "bold"))

def update_guessed():
    if guessed_letters:
        guessed_var.set("NAHULAAN: " + "   ".join(sorted(x.upper() for x in guessed_letters)))
    else:
        guessed_var.set("NAHULAAN: WALA")

def update_stats():
    level_var.set(f"ANTAS {level}")
    combo_var.set(f"SUNOD-SUNOD x{combo}")
    if stats_score_label:
        stats_score_label.config(text=f"PUNTOS {score:,}")
    if stats_wins_label:
        stats_wins_label.config(text=f"PANALO {wins}")
    if stats_losses_label:
        stats_losses_label.config(text=f"TALO {losses}")
    if stats_best_label:
        stats_best_label.config(text=f"PINAKAMAHUSAY NA COMBO x{best_combo}")

def update_lives():
    remaining = max_attempts - wrong_attempts
    attempt_var.set(f"PAGKAKATAON  {remaining}/{max_attempts}")
    if progress_canvas:
        progress_canvas.delete("all")
        w = max(progress_canvas.winfo_width(), 250)
        h = 12
        progress_canvas.create_rectangle(0, 0, w, h, fill="#213E61", outline="")
        ratio = max(0, remaining / max_attempts)
        color = GREEN if ratio > 0.6 else GOLD if ratio > 0.3 else RED
        progress_canvas.create_rectangle(0, 0, int(w * ratio), h, fill=color, outline="")

def update_everything():
    update_word_display()
    update_guessed()
    update_stats()
    update_lives()

# ------------------------------------------------------------
# DRAWING - Filipino-themed gallows with sun/star accents
# ------------------------------------------------------------
def draw_hangman():
    if not hangman_canvas:
        return
    c = hangman_canvas
    c.delete("all")

    # decorative Philippine sun
    cx, cy = 72, 70
    c.create_oval(cx-13, cy-13, cx+13, cy+13, fill=GOLD, outline="")
    for deg in range(0, 360, 45):
        a = math.radians(deg)
        c.create_line(cx + math.cos(a)*18, cy + math.sin(a)*18,
                      cx + math.cos(a)*30, cy + math.sin(a)*30,
                      fill=GOLD, width=3)

    # 3 stars
    for sx, sy in [(45, 135), (72, 150), (99, 135)]:
        c.create_text(sx, sy, text="★", fill=WHITE, font=(FONT, 12, "bold"))

    # bamboo-style frame
    c.create_rectangle(48, 318, 290, 324, fill="#876C3D", outline="")
    c.create_line(68, 318, 68, 55, fill="#C79A57", width=6)
    c.create_line(68, 55, 218, 55, fill="#C79A57", width=6)
    c.create_line(218, 55, 218, 88, fill="#C79A57", width=5)
    c.create_line(68, 96, 110, 55, fill="#A97B43", width=4)

    if wrong_attempts >= 1:
        c.create_oval(188, 88, 248, 148, outline=GOLD, width=4)
        c.create_oval(202, 106, 208, 112, fill=BLUE, outline="")
        c.create_oval(227, 106, 233, 112, fill=RED, outline="")
    if wrong_attempts >= 2:
        c.create_line(218, 148, 218, 235, fill=WHITE, width=6)
    if wrong_attempts >= 3:
        c.create_line(218, 170, 173, 205, fill=BLUE, width=5)
    if wrong_attempts >= 4:
        c.create_line(218, 170, 263, 205, fill=RED, width=5)
    if wrong_attempts >= 5:
        c.create_line(218, 235, 183, 290, fill=GOLD, width=5)
    if wrong_attempts >= 6:
        c.create_line(218, 235, 253, 290, fill=GOLD, width=5)

    if wrong_attempts >= max_attempts and max_attempts < 6:
        if max_attempts == 5:
            c.create_line(218, 235, 253, 290, fill=GOLD, width=5)
        elif max_attempts == 4:
            c.create_line(218, 235, 183, 290, fill=GOLD, width=5)
            c.create_line(218, 235, 253, 290, fill=GOLD, width=5)

    if wrong_attempts >= max_attempts:
        c.create_text(218, 340, text="UBOS NA!", fill=RED_2, font=(FONT, 10, "bold"))
    else:
        c.create_text(218, 340, text="LABAN LANG!", fill=GREEN, font=(FONT, 10, "bold"))

# ------------------------------------------------------------
# EFFECTS
# ------------------------------------------------------------
def floating_text(text, color):
    if not game_root_frame:
        return
    overlay = tk.Label(game_root_frame, text=text, bg=PANEL, fg=color, font=(FONT, 17, "bold"))
    overlay.place(relx=0.72, rely=0.20, anchor="center")
    y = 0.20
    def move(step=0):
        nonlocal y
        if step > 15 or not overlay.winfo_exists():
            try:
                overlay.destroy()
            except Exception:
                pass
            return
        y -= 0.006
        overlay.place_configure(rely=y)
        root.after(25, lambda: move(step + 1))
    move()

def pulse_word():
    if not word_label:
        return
    def sequence(colors, idx=0):
        if not word_label or not word_label.winfo_exists():
            return
        if idx >= len(colors):
            word_label.config(fg=TEXT)
            return
        word_label.config(fg=colors[idx])
        root.after(80, lambda: sequence(colors, idx + 1))
    sequence([GOLD, WHITE, BLUE, TEXT])

# ------------------------------------------------------------
# GAME LOGIC
# ------------------------------------------------------------
def has_won():
    return all((not ch.isalpha()) or (ch in guessed_letters) for ch in current_word)

def disable_game():
    global game_finished
    game_finished = True
    if entry:
        entry.config(state="disabled")
    if guess_button:
        guess_button.config(state="disabled")
    if hint_button:
        hint_button.config(state="disabled")
    for button in letter_buttons.values():
        button.config(state="disabled")

def guess_letter(letter):
    global wrong_attempts, score, wins, losses, combo, best_combo, level

    if game_finished or current_screen != "game" or modal_open:
        return

    letter = letter.lower().strip()
    if len(letter) != 1 or letter not in "abcdefghijklmnopqrstuvwxyz":
        message_var.set("Isang letra lamang ang ilagay.")
        message_label.config(fg=GOLD)
        return

    if letter in guessed_letters:
        message_var.set(f"Nahulaan mo na ang {letter.upper()}.")
        message_label.config(fg=GOLD)
        return

    guessed_letters.add(letter)
    btn = letter_buttons.get(letter)

    if letter in current_word:
        combo += 1
        best_combo = max(best_combo, combo)
        gained = 10 + min(combo - 1, 5) * 2
        score += gained
        if btn:
            btn.config(state="disabled", bg="#124B32", fg=GREEN_2)
        message_var.set(f"TAMA! Nasa salita ang {letter.upper()}.")
        message_label.config(fg=GREEN)
        floating_text(f"+{gained}", GREEN)
        pulse_word()
        sound_correct()
    else:
        combo = 0
        wrong_attempts += 1
        score = max(0, score - 5)
        if btn:
            btn.config(state="disabled", bg="#5B2630", fg="#FF8793")
        message_var.set(f"MALI! Walang {letter.upper()} sa salita.")
        message_label.config(fg=RED_2)
        floating_text("-5", RED_2)
        sound_wrong()

    update_everything()
    draw_hangman()

    if has_won():
        wins += 1
        score += 50
        if wins % 2 == 0:
            level += 1
        update_everything()
        word_var.set("  ".join(ch.upper() if ch != " " else " " for ch in current_word))
        message_var.set("MAHUSAY! NAHULAAN MO ANG SALITA!")
        message_label.config(fg=GREEN)
        disable_game()
        sound_victory()
        fit_word()
        schedule_result(show_victory_overlay)

    elif wrong_attempts >= max_attempts:
        losses += 1
        combo = 0
        update_everything()
        word_var.set("  ".join(ch.upper() if ch != " " else " " for ch in current_word))
        message_var.set("UBOS NA ANG PAGKAKATAON.")
        message_label.config(fg=RED_2)
        disable_game()
        sound_game_over()
        fit_word()
        schedule_result(show_game_over_overlay)

def guess_from_entry():
    if not entry or game_finished:
        return
    letter = entry.get().strip().lower()
    entry.delete(0, tk.END)
    guess_letter(letter)
    if not game_finished and entry:
        entry.focus_set()

def show_hint():
    global score, hint_used
    if game_finished or hint_used:
        return
    score = max(0, score - 5)
    hint_used = True
    if hint_button:
        hint_button.config(state="disabled", text="NAGAMIT NA")
    update_stats()
    sound_hint()
    show_modal(
        "PAHIWATIG",
        f"KATEGORYA\n{current_category}\n\nCLUE\n{current_hint}\n\nKAPALIT: -5 PUNTOS",
        accent=GOLD,
        button_text="BALIK SA LARO"
    )

# ------------------------------------------------------------
# MODALS
# ------------------------------------------------------------
def show_modal(title, body, accent=GOLD, button_text="ISARA"):
    global modal_open
    modal_open = True
    overlay = tk.Frame(app, bg="#020914")
    overlay.place(x=0, y=0, relwidth=1, relheight=1)
    card = tk.Frame(overlay, bg=PANEL, padx=38, pady=32,
                    highlightthickness=2, highlightbackground=accent)
    card.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(card, text=title, bg=PANEL, fg=accent,
             font=(FONT, 20, "bold")).pack(pady=(0, 15))
    tk.Label(card, text=body, bg=PANEL, fg=TEXT, justify="center",
             font=(FONT, 11), wraplength=500).pack(pady=(0, 22))
    def dismiss():
        global modal_open
        modal_open = False
        overlay.destroy()
        if entry and entry.winfo_exists():
            entry.focus_set()
    make_button(card, button_text, dismiss,
                bg_color=accent, fg_color=DARK, hover=accent, width=22).pack()

def show_victory_overlay():
    overlay = tk.Frame(app, bg="#020914")
    overlay.place(x=0, y=0, relwidth=1, relheight=1)
    card = tk.Frame(overlay, bg=PANEL, width=470, height=430,
                    highlightthickness=2, highlightbackground=GREEN)
    card.place(relx=0.5, rely=0.5, anchor="center")
    card.pack_propagate(False)

    tk.Label(card, text="MAHUSAY!", bg=PANEL, fg=GREEN,
             font=(FONT, 12, "bold")).pack(pady=(35, 7))
    tk.Label(card, text="NAHULAAN MO!", bg=PANEL, fg=TEXT,
             font=(FONT, 28, "bold")).pack()
    tk.Label(card, text=current_word.upper(), bg="#123A2A", fg=GREEN_2,
             font=("Courier New", 20, "bold"), padx=18, pady=10).pack(pady=20)
    tk.Label(card, text="★  ★  ★", bg=PANEL, fg=GOLD,
             font=(FONT, 24, "bold")).pack()
    tk.Label(card, text=f"BONUS +50\nKABUUANG PUNTOS {score:,}\nANTAS {level}",
             bg=PANEL, fg=MUTED, font=(FONT, 10, "bold")).pack(pady=14)

    row = tk.Frame(card, bg=PANEL)
    row.pack(pady=8)
    make_button(row, "SUNOD NA SALITA", lambda: (overlay.destroy(), new_game()),
                bg_color=GREEN, fg_color=DARK, hover=GREEN_2).pack(side="left", padx=5)
    make_button(row, "MAIN MENU", lambda: (overlay.destroy(), show_screen("menu")),
                bg_color=PANEL_3, hover="#245E94").pack(side="left", padx=5)

def show_game_over_overlay():
    overlay = tk.Frame(app, bg="#020914")
    overlay.place(x=0, y=0, relwidth=1, relheight=1)
    card = tk.Frame(overlay, bg=PANEL, width=470, height=430,
                    highlightthickness=2, highlightbackground=RED)
    card.place(relx=0.5, rely=0.5, anchor="center")
    card.pack_propagate(False)

    tk.Label(card, text="SAYANG!", bg=PANEL, fg=RED_2,
             font=(FONT, 12, "bold")).pack(pady=(35, 7))
    tk.Label(card, text="UBOS NA!", bg=PANEL, fg=TEXT,
             font=(FONT, 29, "bold")).pack()
    tk.Label(card, text="TAMANG SALITA", bg=PANEL, fg=MUTED,
             font=(FONT, 9, "bold")).pack(pady=(22, 4))
    tk.Label(card, text=current_word.upper(), bg="#3C1B24", fg=RED_2,
             font=("Courier New", 20, "bold"), padx=18, pady=10).pack()
    tk.Label(card, text=f"PUNTOS {score:,}\nPANALO {wins}   •   TALO {losses}",
             bg=PANEL, fg=MUTED, font=(FONT, 10, "bold")).pack(pady=20)

    row = tk.Frame(card, bg=PANEL)
    row.pack()
    make_button(row, "SUBUKAN MULI", lambda: (overlay.destroy(), new_game()),
                bg_color=GOLD, fg_color=DARK, hover="#FFE36E").pack(side="left", padx=5)
    make_button(row, "MAIN MENU", lambda: (overlay.destroy(), show_screen("menu")),
                bg_color=PANEL_3, hover="#245E94").pack(side="left", padx=5)

# ------------------------------------------------------------
# KEYBOARD / CLOSE
# ------------------------------------------------------------
def keyboard_press(event):
    if current_screen != "game" or game_finished:
        return
    if entry and root.focus_get() == entry:
        return
    key = event.char.lower()
    if len(key) == 1 and key.isalpha():
        guess_letter(key)

root.bind("<Key>", keyboard_press)

def on_close():
    global sound_enabled
    sound_enabled = False
    set_music(False)
    cancel_result()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# ------------------------------------------------------------
# START
# ------------------------------------------------------------
root.update_idletasks()
create_particles()
animate_particles()
show_screen("menu")
if __name__ == "__main__":
    set_music(True)
    root.mainloop()
