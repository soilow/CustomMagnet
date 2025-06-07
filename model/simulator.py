import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path

from model.magnet import Magnet
from ui.plot_setup import create_canvas, create_slider
from utils.field_calc import calculate_field


class MagnetModel:
    def __init__(self):
        self.fig, self.ax = create_canvas()
        self.intensity = 5.0
        self.intensity_slider = create_slider(self.fig, self.on_intensity_change)

        self.points = []
        self.positive_pole = None
        self.negative_pole = None
        self.phase = 'draw'
        self.drawing = False
        self.magnets = []

        self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

        self.ax.set_title("Зажмите ЛКМ и нарисуйте магнит. Отпустите — завершится")
        plt.show()

    def on_press(self, event):
        if event.button == 1 and self.phase == 'draw' and event.inaxes == self.ax:
            self.points = [(event.xdata, event.ydata)]
            self.drawing = True

    def on_motion(self, event):
        if self.drawing and event.xdata is not None and event.ydata is not None and event.inaxes == self.ax:
            self.points.append((event.xdata, event.ydata))
            if len(self.points) > 1:
                x_prev, y_prev = self.points[-2]
                x_curr, y_curr = self.points[-1]
                self.ax.plot([x_prev, x_curr], [y_prev, y_curr], color='red', linewidth=1.5)
                self.fig.canvas.draw()

    def on_release(self, event):
        if not self.drawing or event.inaxes != self.ax:
            return

        self.drawing = False
        self.phase = 'poles'
        self.polygon = Path(self.points)
        x0, y0 = self.points[0]
        x1, y1 = self.points[-1]
        self.ax.plot([x1, x0], [y1, y0], color='red', linewidth=1.5)
        self.ax.fill(*zip(*self.points), color='gray', alpha=0.2)
        self.ax.set_title("Кликните внутри: сначала ПЛЮС, потом МИНУС")
        self.fig.canvas.draw()

        self.fig.canvas.mpl_disconnect(self.cid_press)
        self.fig.canvas.mpl_disconnect(self.cid_release)
        self.fig.canvas.mpl_disconnect(self.cid_motion)
        self.cid_pole_click = self.fig.canvas.mpl_connect('button_press_event', self.on_pole_click)

    def on_pole_click(self, event):
        if event.xdata is None or event.ydata is None:
            return

        point = np.array([event.xdata, event.ydata])
        if not self.polygon.contains_point(point):
            self.ax.set_title("Полюс должен быть внутри фигуры")
            self.fig.canvas.draw()
            return

        if self.positive_pole is None:
            self.positive_pole = point
            self.ax.text(*point, '+', color='red', fontsize=16, ha='center', va='center', fontweight='bold')
            self.ax.set_title("Укажите МИНУС (южный полюс)")
            self.fig.canvas.draw()
        elif self.negative_pole is None:
            self.negative_pole = point
            self.ax.text(*point, '-', color='blue', fontsize=16, ha='center', va='center', fontweight='bold')

            self.magnets.append(Magnet(self.points, self.positive_pole, self.negative_pole))

            self.points = []
            self.positive_pole = None
            self.negative_pole = None
            self.phase = 'draw'

            self.ax.set_title("Магнит добавлен. Нарисуйте новый или измените интенсивность")
            self.fig.canvas.mpl_disconnect(self.cid_pole_click)
            self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
            self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
            self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

            self.process_field()

    def on_intensity_change(self, val):
        self.intensity = val
        if self.magnets:
            self.process_field()

    def process_field(self):
        self.ax.cla()
        self.ax.set_xlim(-6, 6)
        self.ax.set_ylim(-6, 6)
        self.ax.set_aspect('equal')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.ax.grid(False)

        valid_magnets = [m for m in self.magnets if len(m.points) >= 3]

        if not valid_magnets:
            self.ax.set_title("Нет валидных магнитов для отображения")
            self.fig.canvas.draw()
            return

        for magnet in valid_magnets:
            self.ax.fill(*zip(*magnet.points), color='gray', alpha=0.2)
            for i in range(len(magnet.points) - 1):
                x0, y0 = magnet.points[i]
                x1, y1 = magnet.points[i + 1]
                self.ax.plot([x0, x1], [y0, y1], color='red', linewidth=1.5)
            x0, y0 = magnet.points[0]
            x1, y1 = magnet.points[-1]
            self.ax.plot([x1, x0], [y1, y0], color='red', linewidth=1.5)
            self.ax.text(*magnet.positive_pole, '+', color='red', fontsize=16, ha='center', va='center', fontweight='bold')
            self.ax.text(*magnet.negative_pole, '−', color='blue', fontsize=16, ha='center', va='center', fontweight='bold')

        x = np.linspace(-6, 6, 150)
        y = np.linspace(-6, 6, 150)
        X, Y = np.meshgrid(x, y)

        Bx, By = calculate_field(valid_magnets, X, Y, self.intensity)

        density = 1.0 + 0.3 * self.intensity
        linewidth = 0.5 + 0.1 * self.intensity

        self.ax.streamplot(x, y, Bx, By,
                           color=np.hypot(Bx, By),
                           linewidth=linewidth,
                           density=density,
                           cmap='plasma')
        self.ax.set_title("Кол-во магнитов: " + str(len(valid_magnets)))
        self.fig.canvas.draw()
