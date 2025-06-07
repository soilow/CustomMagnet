import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def create_canvas():
    fig, ax = plt.subplots(figsize=(12, 10))
    fig.patch.set_facecolor('#f7f8fa')
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.set_aspect('equal')
    ax.set_facecolor('white')
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)
    return fig, ax

def create_slider(fig, callback):
    slider_ax = fig.add_axes([0.25, 0.03, 0.5, 0.02])
    slider = Slider(slider_ax, 'Интенсивность магнитного поля', 0.1, 20.0, valinit=5.0, valstep=0.1)
    slider.on_changed(callback)
    return slider
