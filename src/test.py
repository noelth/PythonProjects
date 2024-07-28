from pynput import mouse
This is edit file and after staged
added something here
# Define the event handler functions
def on_click(x, y, button, pressed):
    print(f"The button is: {pressed} ")
    if pressed:
        print(f"Mouse button {button} pressed at ({x}, {y})")
    else:
        print(f"Mouse button {button} released at ({x}, {y})")

def on_scroll(x, y, dx, dy):
    print(f"Mouse scrolled at ({x}, {y}) with delta ({dx}, {dy})")

def on_move(x, y):
    print(f"Mouse moved to ({x}, {y})")

# Set up the listener
with mouse.Listener(on_click=on_click, on_scroll=on_scroll, on_move=on_move) as listener:
    print("Mouse event listener started")
    listener.join()