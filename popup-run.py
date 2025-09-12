import tkinter as tk
import random
import time
import sys

if sys.platform == "win32":
    import winsound

typed = ""
button_pressed = False
runaway_active = True
last_toggle_time = time.time()

error_popups_to_spawn = 1
total_popups_spawned = 0
max_total_popups = 100  # Max popups
pause_after_limit = False

btn_start_x = 0
btn_start_y = 0

hover_teleport_after_ms = 500
stay_put_after_teleport_ms = 1000

hover_job = None
stay_put = False

mute_sounds = False
popups_paused = False
popup_windows = []

alt_f4_pressed = False  # flag if Alt+F4 pressed to keep flashing white, not red

def play_error_sound():
    if sys.platform == "win32" and not mute_sounds:
        winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)

def play_shutdown_sound():
    if sys.platform == "win32" and not mute_sounds:
        winsound.PlaySound("SystemExit", winsound.SND_ALIAS | winsound.SND_ASYNC)

def change_bg_button():
    global button_pressed, win, label
    play_shutdown_sound()

    btn.place(x=btn_start_x, y=btn_start_y)

    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    win.configure(bg=color)
    label.configure(bg=color)

    if not button_pressed:
        button_pressed = True
        label.configure(fg="white")

def change_bg_alt_f4():
    global win, label, alt_f4_pressed
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    win.configure(bg=color)
    label.configure(bg=color)
    alt_f4_pressed = True  # enable flashing white instead of red

def is_overlapping(x1, y1, w1, h1, x2, y2, w2, h2):
    return not (x1 + w1 < x2 or x1 > x2 + w2 or y1 + h1 < y2 or y1 > y2 + h2)

def get_random_popup_position(popup_w, popup_h):
    ww = win.winfo_width()
    wh = win.winfo_height()

    forbidden_x1 = ww * 0.25
    forbidden_x2 = ww * 0.75
    forbidden_y1 = wh * 0.3
    forbidden_y2 = wh * 0.6

    btn_x = btn.winfo_x()
    btn_y = btn.winfo_y()
    btn_w = btn.winfo_width()
    btn_h = btn.winfo_height()

    attempts = 0
    max_attempts = 100
    while attempts < max_attempts:
        x = random.randint(0, ww - popup_w)
        y = random.randint(0, wh - popup_h)

        if is_overlapping(x, y, popup_w, popup_h,
                          forbidden_x1, forbidden_y1,
                          forbidden_x2 - forbidden_x1,
                          forbidden_y2 - forbidden_y1):
            attempts += 1
            continue

        if is_overlapping(x, y, popup_w, popup_h,
                          btn_x, btn_y, btn_w, btn_h):
            attempts += 1
            continue

        return x, y

    return 0, wh - popup_h - 50

def show_error_popup(message, title="HACKED"):
    global popup_windows

    popup = tk.Toplevel(win)
    popup.title(title)
    popup.configure(bg='white')
    popup.resizable(False, False)
    popup.geometry("250x120")
    popup.attributes('-topmost', True)

    popup.update_idletasks()
    popup_w = 250
    popup_h = 120

    x, y = get_random_popup_position(popup_w, popup_h)
    popup.geometry(f"{popup_w}x{popup_h}+{x + win.winfo_x()}+{y + win.winfo_y()}")

    icon_label = tk.Label(popup, text="⚠️", font=("Arial", 30), bg='white', fg='red')
    icon_label.pack(side="left", padx=10, pady=20)

    msg_label = tk.Label(popup, text=message, font=("Arial", 14), bg='white')
    msg_label.pack(side="left", padx=10)

    def close_popup():
        play_shutdown_sound()
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        win.configure(bg=color)
        label.configure(bg=color)
        if popup in popup_windows:
            popup_windows.remove(popup)
        popup.destroy()
        try:
            win.focus_force()
        except:
            pass

    close_btn = tk.Button(popup, text="OK", command=close_popup)
    close_btn.pack(side="bottom", pady=10)

    def refocus_main_window():
        try:
            win.focus_force()
        except:
            pass

    popup.after(1000, lambda: (popup.destroy(), refocus_main_window()))
    popup_windows.append(popup)

def spawn_popup_batch(batch, index=0):
    global total_popups_spawned, pause_after_limit, popups_paused
    if pause_after_limit or index >= len(batch) or popups_paused:
        return

    show_error_popup("HACKED", "HACKED")
    total_popups_spawned += 1

    if total_popups_spawned >= max_total_popups:
        pause_after_limit = True
        try:
            win.focus_force()
        except:
            pass
        win.after(500, reset_error_cycle)
        return

    win.after(250, spawn_popup_batch, batch, index + 1)

def delayed_play_sound():
    play_error_sound()

def spawn_error_popups():
    global error_popups_to_spawn, popups_paused

    if pause_after_limit or popups_paused:
        return

    to_spawn = min(error_popups_to_spawn, max_total_popups - total_popups_spawned)
    batch = list(range(to_spawn))

    win.after(150, delayed_play_sound)

    spawn_popup_batch(batch)

    error_popups_to_spawn *= 2
    win.after(400, spawn_error_popups)

def reset_error_cycle():
    global error_popups_to_spawn, total_popups_spawned, pause_after_limit
    error_popups_to_spawn = 1
    total_popups_spawned = 0
    pause_after_limit = False
    spawn_error_popups()

def check_close(event):
    global typed, win, mute_sounds, popups_paused, popup_windows, alt_f4_pressed

    key = event.keysym.lower()
    char = event.char.lower() if event.char else ""

    typed += char
    typed = typed[-5:]

    # Fix exit and close detection (only when typed, not keysym)
    if typed == "close" or typed == "exit":
        play_shutdown_sound()
        win.destroy()
        return

    if key == "m":
        global mute_sounds
        mute_sounds = not mute_sounds

    elif key == "o":
        global popups_paused, error_popups_to_spawn, total_popups_spawned, pause_after_limit
        popups_paused = not popups_paused
        if popups_paused:
            # Clear all popups
            for pw in popup_windows[:]:
                try:
                    pw.destroy()
                except:
                    pass
            popup_windows.clear()
        else:
            # Reset counters and restart popups when unpaused
            error_popups_to_spawn = 1
            total_popups_spawned = 0
            pause_after_limit = False
            spawn_error_popups()

def flash_label():
    # Flash text:
    # If alt_f4 pressed => flash white <-> bg color (never red)
    # Else flash red <-> bg color (unless button pressed, then white <-> bg color)
    if alt_f4_pressed:
        current_color = label.cget("fg")
        label.configure(fg=win.cget("bg") if current_color == "white" else "white")
    else:
        if button_pressed:
            current_color = label.cget("fg")
            label.configure(fg=win.cget("bg") if current_color == "white" else "white")
        else:
            current_color = label.cget("fg")
            label.configure(fg=win.cget("bg") if current_color == "red" else "red")
    label.after(150, flash_label)

def on_mouse_move(event):
    global btn, runaway_active, stay_put
    if not runaway_active or stay_put:
        return
    try:
        bx, by = btn.winfo_rootx(), btn.winfo_rooty()
        bw, bh = btn.winfo_width(), btn.winfo_height()
        mx, my = event.x_root, event.y_root
        distance = ((mx - (bx + bw/2))**2 + (my - (by + bh/2))**2) ** 0.5
        if distance < 150:
            move_button()
    except:
        pass

def move_button():
    global btn, win, label
    win.update_idletasks()
    ww, wh = win.winfo_width(), win.winfo_height()
    bw, bh = btn.winfo_width(), btn.winfo_height()

    label_x = label.winfo_x()
    label_y = label.winfo_y()
    label_w = label.winfo_width()
    label_h = label.winfo_height()

    forbidden_x1 = label_x - bw
    forbidden_y1 = label_y - bh
    forbidden_x2 = label_x + label_w + bw
    forbidden_y2 = label_y + label_h + bh

    attempts = 0
    max_attempts = 100
    while attempts < max_attempts:
        new_x = random.randint(0, ww - bw)
        new_y = random.randint(0, wh - bh)

        if is_overlapping(new_x, new_y, bw, bh,
                          forbidden_x1, forbidden_y1,
                          forbidden_x2 - forbidden_x1,
                          forbidden_y2 - forbidden_y1):
            attempts += 1
            continue
        break

    btn.place(x=new_x, y=new_y)

def on_btn_enter(event):
    global hover_job
    if hover_job is None:
        hover_job = win.after(hover_teleport_after_ms, teleport_btn_back)

def on_btn_leave(event):
    global hover_job
    if hover_job is not None:
        win.after_cancel(hover_job)
        hover_job = None

def teleport_btn_back():
    global btn, btn_start_x, btn_start_y, runaway_active, stay_put, hover_job
    hover_job = None
    btn.place(x=btn_start_x, y=btn_start_y)
    runaway_active = False
    stay_put = True

def resume_runaway():
    global runaway_active, stay_put
    runaway_active = True
    stay_put = False
    win.after(stay_put_after_teleport_ms, resume_runaway)

def toggle_runaway_loop():
    global runaway_active, last_toggle_time
    now = time.time()
    elapsed = now - last_toggle_time
    if runaway_active and elapsed >= 10:
        runaway_active = False
        last_toggle_time = now
    elif not runaway_active and elapsed >= 2:
        runaway_active = True
        last_toggle_time = now
    win.after(100, toggle_runaway_loop)

def create_window():
    global win, label, btn, btn_start_x, btn_start_y

    win = tk.Tk()
    win.title("L BOZO")
    win.attributes("-fullscreen", True)
    win.configure(bg="black")
    win.focus_set()

    label = tk.Label(
        win,
        text="⚠️ L BOZO ⚠️",
        fg="red",
        bg="black",
        font=("Arial", 60, "bold"),
        wraplength=1000
    )
    label.place(relx=0.5, rely=0.5, anchor="center")

    btn = tk.Button(
        win,
        text="CLOSE",
        font=("Arial", 24),
        command=change_bg_button,
        bg="darkred",
        fg="white"
    )

    win.update_idletasks()
    bw = btn.winfo_reqwidth()
    bh = btn.winfo_reqheight()
    ww = win.winfo_screenwidth()
    wh = win.winfo_screenheight()

    btn_start_x = (ww - bw) // 2
    btn_start_y = int(wh * 0.5 + 120)
    btn.place(x=btn_start_x, y=btn_start_y)

    btn.bind("<Enter>", on_btn_enter)
    btn.bind("<Leave>", on_btn_leave)

    win.bind('<Motion>', on_mouse_move)
    win.bind("<Key>", check_close)
    win.protocol("WM_DELETE_WINDOW", change_bg_alt_f4)

    toggle_runaway_loop()
    flash_label()
    spawn_error_popups()

    win.mainloop()

create_window()
