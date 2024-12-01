import socket
import subprocess
import queue
import math
import time
import math
import trimesh
import board
import busio
import digitalio
import adafruit_ssd1306

import numpy as np

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = None
port = 5000
try:
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
except socket.error as e:
    ip = "127.0.0.1"
finally:
    s.close()

wifi = None
try:
    result = subprocess.check_output(
        ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in result.split("\n"):
        if line.startswith("yes"):
            wifi = line.split(":")[1]
except Exception as e:
    print("Error")


class Volumetric_Display:
    def __init__(self, dimensions, spi, pins):
        self.width = dimensions["width"]
        self.height = dimensions["height"]
        self.length = len(pins)

        self.oleds = [
            adafruit_ssd1306.SSD1306_SPI(
                self.width,
                self.height,
                busio.SPI(spi["sclk"], spi["mosi"], spi["miso"]),
                digitalio.DigitalInOut(pin["dc"]),
                digitalio.DigitalInOut(pin["reset"]),
                digitalio.DigitalInOut(pin["cs"]),
            )
            for pin in pins
        ]

    def clear(self):
        for oled in self.oleds:
            oled.fill(0)
            oled.show()

    def line(self, start, end):
        x1, y1, z1 = start
        x2, y2, z2 = end

        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1

        steps = max(abs(dx), abs(dy), abs(dz))

        x_increment = dx / steps if steps > 0 else 0
        y_increment = dy / steps if steps > 0 else 0
        z_increment = dz / steps if steps > 0 else 0

        points = []
        for i in range(steps + 1):
            x = int(round(x1 + i * x_increment))
            y = int(round(y1 + i * y_increment))
            z = int(round(z1 + i * z_increment))
            points.append((x, y, z))

        for point in points:
            x, y, z = point
            if (z < 0) or (z > 5):
                continue
            self.oleds[z].pixel(x, y, 1)

    def load_mesh(self, filepath):
        mesh = trimesh.load_mesh(filepath)
        return mesh.vertices / 2, mesh.faces

    def center_vertices(self, vertices, width, height, length, axis, speed):
        t = (time.time() / 10.0) * float(speed)
        angle = t % (2 * math.pi)

        rotation_matrix = None

        if axis == "X":
            rotation_matrix = np.array(
                [
                    [1, 0, 0],
                    [0, math.cos(angle), -math.sin(angle)],
                    [0, math.sin(angle), math.cos(angle)],
                ]
            )
        elif axis == "Y":
            rotation_matrix = np.array(
                [
                    [math.cos(angle), 0, math.sin(angle)],
                    [0, 1, 0],
                    [-math.sin(angle), 0, math.cos(angle)],
                ]
            )
        elif axis == "Z":
            rotation_matrix = np.array(
                [
                    [math.cos(angle), -math.sin(angle), 0],
                    [math.sin(angle), math.cos(angle), 0],
                    [0, 0, 1],
                ]
            )

        rotated_vertices = np.dot(vertices, rotation_matrix.T)

        scaled_vertices = rotated_vertices * np.array([height, height, length])

        centroid = scaled_vertices.mean(axis=0)

        bbox_center = np.array([width / 2, height / 2, length / 2])
        centered_vertices = scaled_vertices - centroid + bbox_center

        return centered_vertices

    def create_lines_from_faces(self, vertices, faces):
        lines = []
        for face in faces:
            for i in range(len(face)):
                i1 = face[i]
                i2 = face[(i + 1) % len(face)]
                line = (tuple(vertices[i1]), tuple(vertices[i2]))
                lines.append(line)
        return lines

    def draw_model(self, file_path, axis, speed, q, width=128, height=64, length=5):
        vertices, faces = self.load_mesh(file_path)
        while True:
            vertexes = self.center_vertices(
                vertices, width, height, length, axis, speed
            )
            lines = self.create_lines_from_faces(vertexes, faces)
            for l in lines:
                start = (int(l[0][0]), int(l[0][1]), int(l[0][2]))
                end = (int(l[1][0]), int(l[1][1]), int(l[1][2]))
                self.line(start, end)

            for oled in self.oleds:
                oled.show()
                oled.fill(0)

            if q.empty():
                pass
            else:
                return


DIMENSIONS = {"width": 128, "height": 64}
SPI = {
    "sclk": board.SCLK,
    "mosi": board.MOSI,
    "miso": board.MISO,
}
PINS = [
    {"dc": board.D4, "reset": board.D3, "cs": board.D2},
    {"dc": board.D18, "reset": board.D15, "cs": board.D14},
    {"dc": board.D22, "reset": board.D27, "cs": board.D17},
    {"dc": board.D6, "reset": board.D5, "cs": board.D0},
    {"dc": board.D26, "reset": board.D19, "cs": board.D13},
    {"dc": board.D21, "reset": board.D20, "cs": board.D16},
]

volumetric_display = Volumetric_Display(DIMENSIONS, SPI, PINS)

def wall():
    for _ in range(3):
        for oled in volumetric_display.oleds:
            oled.fill(1)
            oled.show()
            time.sleep(0.1)
            oled.fill(0)
            oled.show()

        for oled in volumetric_display.oleds[::-1]:
            oled.fill(1)
            oled.show()
            time.sleep(0.1)
            oled.fill(0)
            oled.show()

    volumetric_display.clear()


def sauron():
    volumetric_display.clear()
    start = time.time()
    end = time.time()
    while end - start < 10:
        for idx, oled in enumerate(volumetric_display.oleds):
            t = int(8 * (idx + 1) * math.sin(time.time() / 1.5))
            oled.circle(64, 32, 32 + t, 1)
            oled.show()
            time.sleep(0.05)

        end = time.time()


def plane():
    start = time.time()
    end = time.time()
    while end - start < 5:
        for oled in volumetric_display.oleds:
            oled.fill(0)

        for i in range(volumetric_display.width):
            volumetric_display.line(
                (i, int(math.cos(time.time()) * 32 + 32), 0),
                (i, 64 - int(math.cos(time.time()) * 32 + 32), 5),
            )

        for oled in volumetric_display.oleds:
            oled.show()

        end = time.time()


def run_reader(q):
    item = None

    volumetric_display.clear()
    volumetric_display.oleds[0].text(wifi, 0, 0, 1)
    volumetric_display.oleds[0].text(ip + ":" + str(port), 0, 10, 1)
    volumetric_display.oleds[0].show()
    while q.empty() == True:
        time.sleep(1)
    volumetric_display.clear()

    while True:

        try:
            item = q.get(block=False)
        except queue.Empty:
            continue

        if item != None:

            if item["file"][-3:] == "obj":
                volumetric_display.draw_model(
                    "./uploads/" + item["file"], item["axis"], item["speed"], q
                )

            elif item["file"] == "wall":
                while q.empty():
                    wall()
            elif item["file"] == "plane":
                while q.empty():
                    plane()
            elif item["file"] == "sauron":
                while q.empty():
                    sauron()

        time.sleep(1)
