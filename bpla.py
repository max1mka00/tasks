import pygame
import math
import datetime
import folium
from folium.features import CustomIcon
from pygame.locals import *
from flightgear_python.fg_if import TelnetConnection
from flightgear_python.fg_if import GuiConnection

pygame.init()
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Helicopter Instruments Panel")
clock = pygame.time.Clock()

COLORS = {
    "background": (100, 100, 100),
    "sensor_ok": (0, 100, 0),
    "sensor_bad": (100, 0, 0),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "sky": (0, 21, 140),
    "ground": (139, 69, 19),
    "red": (255, 0, 0),
    "yellow": (255, 255, 0)
}

def gui_callback(gui_data, event_pipe):
    lat_deg = math.degrees(gui_data['lat_rad'])
    lon_deg = math.degrees(gui_data['lon_rad'])
    alt_m = gui_data['alt_m']
    agl_m = gui_data['agl_m']
    phi_rad = gui_data['phi_rad']
    theta_rad = gui_data['theta_rad']
    psi_rad = gui_data['psi_rad']
    climb_rate = gui_data['climb_rate_ft_per_s']
    child_data = (lat_deg, lon_deg, alt_m, agl_m, phi_rad, theta_rad, psi_rad, climb_rate)
    event_pipe.child_send(child_data)

def draw_top_sensors(surface, sensor_data):
    sensor_width = 100
    sensor_height = 30
    spacing = 10
    total_width = 10 * sensor_width + 9 * spacing
    start_x = (1200 - total_width) // 2
    start_y = 20
    font_size = 16
    font = pygame.font.Font(None, font_size)
    for i in range(10):
        x = start_x + i * (sensor_width + spacing)
        if i < len(sensor_data):
            sensor = sensor_data[i]
            color = COLORS["sensor_ok"] if not sensor["value"] else COLORS["sensor_bad"]
            abbreviation = sensor["abbreviation"]
        else:
            color = COLORS["sensor_ok"]
            abbreviation = ""

        pygame.draw.rect(surface, color, (x, start_y, sen-sor_width, sensor_height))
        pygame.draw.line(surface, COLORS["white"], (x, start_y), (x + sensor_width, start_y), 2)
        pygame.draw.line(surface, COLORS["white"], (x, start_y), (x, start_y + sensor_height), 2)
        pygame.draw.line(surface, COLORS["black"], (x + sen-sor_width, start_y),
                         (x + sensor_width, start_y + sen-sor_height), 2)
        pygame.draw.line(surface, COLORS["black"], (x, start_y + sensor_height),
                         (x + sensor_width, start_y + sen-sor_height), 2)


        text_surface = font.render(abbreviation, True, COL-ORS["white"])
        text_rect = text_surface.get_rect(center=(x + sen-sor_width // 2, start_y + sensor_height // 2))
        surface.blit(text_surface, text_rect)


def draw_attitude_indicator(surface, roll_rad, pitch_rad, x, y, size):
    roll_deg = -math.degrees(roll_rad)
    pitch_deg = math.degrees(pitch_rad)
    radius = size // 2
    border_width = 15

    container = pygame.Surface((size, size), pygame.SRCALPHA)

    inner_width = int(size * 1.5)
    inner_height = int(size * 2)
    inner = pygame.Surface((inner_width, inner_height), pygame.SRCALPHA)
    pitch_offset = int(pitch_deg * 2.0)
    sky_height = inner.get_height() // 2 - pitch_offset

    pygame.draw.rect(inner, COLORS["sky"], (0, 0, inner_width, sky_height))
    pygame.draw.rect(inner, COLORS["ground"], (0, sky_height, inner_width, inner_height - sky_height))

    rotated_inner = pygame.transform.rotate(inner, roll_deg)
    rot_rect = rotated_inner.get_rect(center=(radius, radius))
    container.blit(rotated_inner, rot_rect.topleft)

    for angle in range(-180, 180, 10):
        rad_angle = math.radians(angle + roll_deg)
        start_out = (radius + (radius - border_width) * math.cos(rad_angle),
                     radius + (radius - border_width) * math.sin(rad_angle))

        if angle % 30 == 0:

            length = 15
            end = (radius + (radius - border_width - length) * math.cos(rad_angle),
                   radius + (radius - border_width - length) * math.sin(rad_angle))
            pygame.draw.line(container, COLORS["white"], start_out, end, 2)

            text = font.render(str(abs(angle)), True, COL-ORS["white"])
            text_rect = text.get_rect(center=(
                radius + (radius - border_width - length - 10) * math.cos(rad_angle),
                radius + (radius - border_width - length - 10) * math.sin(rad_angle)
            ))
            container.blit(text, text_rect)
        else:
            length = 8
            end = (radius + (radius - border_width - length) * math.cos(rad_angle),
                   radius + (radius - border_width - length) * math.sin(rad_angle))
            pygame.draw.line(container, COLORS["white"], start_out, end, 2)

    pitch_marker_lengths = {
        5: 10,
        10: 15,
        20: 20
    }

    for pitch_angle in range(-20, 21, 5):
        if pitch_angle == 0:
            continue

        if abs(pitch_angle) == 20:
            length = pitch_marker_lengths[20]
        elif abs(pitch_angle) % 10 == 0:
            length = pitch_marker_lengths[10]
        else:
            length = pitch_marker_lengths[5]

        y_offset = pitch_angle * 2.5
        y_pos = radius + y_offset - pitch_offset

        if abs(pitch_angle) == 20:
            pygame.draw.line(container, COLORS["white"],
                             (radius - length, y_pos), (radius + length, y_pos), 2)
            text = font.render(f"{abs(pitch_angle)}", True, COLORS["white"])
            text_rect = text.get_rect(center=(radius - length - 15, y_pos))
            container.blit(text, text_rect)
            text_rect = text.get_rect(center=(radius + length + 15, y_pos))
            container.blit(text, text_rect)
        elif abs(pitch_angle) % 10 == 0:
            pygame.draw.line(container, COLORS["white"],
                             (radius - length, y_pos), (radius + length, y_pos), 2)
            text = font.render(f"{abs(pitch_angle)}", True, COLORS["white"])
            text_rect = text.get_rect(center=(radius - length - 15, y_pos))
            container.blit(text, text_rect)
            text_rect = text.get_rect(center=(radius + length + 15, y_pos))
            container.blit(text, text_rect)
        else:
            pygame.draw.line(container, COLORS["white"],
                             (radius - length, y_pos), (radius + length, y_pos), 2)

    pygame.draw.circle(container, COLORS["red"], (radius, ra-dius), 6)

    strip_length = 40
    strip_thickness = 6
    strip_offset = 30

    pygame.draw.rect(container, COLORS["yellow"],
                     (radius - strip_offset - strip_length, radius - strip_thickness // 2,
                      strip_length, strip_thickness))

    pygame.draw.rect(container, COLORS["yellow"],
                     (radius + strip_offset, radius - strip_thickness // 2,
                      strip_length, strip_thickness))

    pygame.draw.circle(container, COLORS["black"], (radius, radius), radius, border_width)
    pygame.draw.circle(container, COLORS["background"], (radi-us, radius), radius+64, border_width+50)
    surface.blit(container, (x, y))


def draw_heading_indicator(surface, heading_rad, x, y, size):
    radius = size // 2
    border_width = 5
    font = pygame.font.Font(None, 24)

    container = pygame.Surface((size, size), pygame.SRCALPHA)

    pygame.draw.circle(container, COLORS["white"], (radius, radius), radius, border_width)

    pygame.draw.circle(container, COLORS["black"], (radius, radius), radius - border_width)

    heading_deg = math.degrees(heading_rad)
    for angle in range(0, 360, 10):
        draw_angle = angle - 90 - heading_deg
        rad_angle = math.radians(draw_angle)

        if angle % 30 == 0:
            length = 15
            if angle == 0:
                text_str = "N"
            elif angle == 90:
                text_str = "E"
            elif angle == 180:
                text_str = "S"
            elif angle == 270:
                text_str = "W"
            else:
                text_str = str(angle // 10)

            text = font.render(text_str, True, COL-ORS["white"])
            text_rect = text.get_rect(
                center=(radius + (radius - 30) * math.cos(rad_angle),
                        radius + (radius - 30) * math.sin(rad_angle)))
            container.blit(text, text_rect)
        else:
            length = 8

        start = (radius + (radius - border_width) * math.cos(rad_angle),
                 radius + (radius - border_width) * math.sin(rad_angle))
        end = (radius + (radius - border_width - length) * math.cos(rad_angle),
               radius + (radius - border_width - length) * math.sin(rad_angle))
        pygame.draw.line(container, COLORS["white"], start, end, 2)

    arrow_angle = math.radians(-90)
    arrow_points = [
        (radius + (radius - 20) * math.cos(arrow_angle),
         radius + (radius - 20) * math.sin(arrow_angle)),
        (radius + 10 * math.cos(arrow_angle + math.radians(150)),
         radius + 10 * math.sin(arrow_angle + math.radians(150))),
        (radius + 10 * math.cos(arrow_angle - math.radians(150)),
         radius + 10 * math.sin(arrow_angle - math.radians(150)))
    ]
    pygame.draw.polygon(container, COLORS["white"], ar-row_points)

    label_text = font.render("КУРС", True, COLORS["yellow"])
    label_rect = label_text.get_rect(topright=(size -75, 120))
    container.blit(label_text, label_rect)

    surface.blit(container, (x, y))


def draw_speed_indicator(surface, speed, x, y, size):
    radius = size // 2
    border_width = 5
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)

    container = pygame.Surface((size, size), pygame.SRCALPHA)

    pygame.draw.circle(container, COLORS["white"], (radius, radius), radius, border_width)

    pygame.draw.circle(container, COLORS["black"], (radius, radius), radius - border_width)

    label_text = small_font.render("узлы", True, COL-ORS["yellow"])
    label_rect = label_text.get_rect(topright=(size - 35, 35))
    container.blit(label_text, label_rect)

    max_speed = 300
    start_angle = -90
    scale_range = 270

    for speed_mark in range(0, 301, 20):

        angle = start_angle - (speed_mark / max_speed) * scale_range
        rad_angle = math.radians(angle)

        if speed_mark % 100 == 0:
            length = 15
            text = font.render(str(speed_mark), True, COL-ORS["white"])
            text_rect = text.get_rect(
                center=(radius + (radius - 35) * math.cos(rad_angle),
                        radius + (radius - 35) * math.sin(rad_angle)))
            container.blit(text, text_rect)
        else:
            length = 8

        start = (radius + (radius - border_width) * math.cos(rad_angle),
                 radius + (radius - border_width) * math.sin(rad_angle))
        end = (radius + (radius - border_width - length) * math.cos(rad_angle),
               radius + (radius - border_width - length) * math.sin(rad_angle))
        pygame.draw.line(container, COLORS["white"], start, end, 2)

        arrow_angle = start_angle - (speed / max_speed) * scale_range
        rad_angle = math.radians(arrow_angle)

        arrow_length = radius - 25
        arrow_points = [
            (radius + arrow_length * math.cos(rad_angle),
             radius + arrow_length * math.sin(rad_angle)),
            radius + 10 * math.cos(rad_angle + math.radians(150)),
             radius + 10 * math.sin(rad_angle + math.radians(150)),
             radius + 10 * math.cos(rad_angle - math.radians(150)),
              radius + 10 * math.sin(rad_angle - math.radians(150))
             ]
        pygame.draw.polygon(container, COLORS["white"], [
             arrow_points[0],
             (arrow_points[1], arrow_points[2]),
            (arrow_points[3], arrow_points[4])
        ])

        text = font.render(f"{int(speed)}", True, COL-ORS["white"])
        text_rect = text.get_rect(center=(radius + 48, radius - 35))
        container.blit(text, text_rect)

        surface.blit(container, (x, y))


def draw_vsi_indicator(surface, vs, x, y, size):
    radius = size // 2
    border_width = 5
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 16)
    small_font1 = pygame.font.Font(None, 18)
    max_vs = 20

    container = pygame.Surface((size, size), pygame.SRCALPHA)

    pygame.draw.circle(container, COLORS["white"], (radius, radius), radius, border_width)

    pygame.draw.circle(container, COLORS["black"], (radius, radius), radius - border_width)

    label_text1 = small_font.render("ВЕРТИКАЛЬНАЯ СКОРОСТЬ", True, COLORS["yellow"])
    label_rect1 = label_text1.get_rect(topright=(size - 20, 55))
    container.blit(label_text1, label_rect1)

    label_text2 = small_font.render("М/С", True, COL-ORS["white"])
    label_rect2 = label_text2.get_rect(topright=(size -90, 70))
    container.blit(label_text2, label_rect2)

    label_text3 = small_font1.render("вверх", True, COL-ORS["white"])
    label_rect3 = label_text3.get_rect(topright=(size -130, 70))
    container.blit(label_text3, label_rect3)

    label_text4 = small_font1.render("вниз", True, COL-ORS["white"])
    label_rect4 = label_text4.get_rect(topright=(size -135, 120))
    container.blit(label_text4, label_rect4)

    start_angle = -180
    scale_range = 180

    for angle in range(-180, 181, 90):
        rad_angle = math.radians(angle)
        start = (radius + (radius - border_width) * math.cos(rad_angle),
                 radius + (radius - border_width) * math.sin(rad_angle))
        end = (radius + (radius - border_width - 15) * math.cos(rad_angle),
               radius + (radius - border_width - 15) * math.sin(rad_angle))
        pygame.draw.line(container, COLORS["white"], start, end, 2)

    for vs_mark in range(-20, 21, 2):
        angle = start_angle + (vs_mark / max_vs) * scale_range
        rad_angle = math.radians(angle)

        if vs_mark % 10 == 0:
            length = 15
            text = font.render(str(abs(vs_mark)), True, COL-ORS["white"])
            text_rect = text.get_rect(
                center=(radius + (radius - 30) * math.cos(rad_angle),
                        radius + (radius - 30) * math.sin(rad_angle)))
            container.blit(text, text_rect)
        else:
            length = 8

            start = (radius + (radius - border_width) * math.cos(rad_angle),
                     radius + (radius - border_width) * math.sin(rad_angle))
            end = (radius + (radius - border_width - length) * math.cos(rad_angle),
                   radius + (radius - border_width - length) * math.sin(rad_angle))
            pygame.draw.line(container, COLORS["white"], start, end, 2)

            arrow_angle = start_angle + (vs / max_vs) * scale_range
            rad_angle = math.radians(arrow_angle)

            arrow_length = radius - 25
            arrow_points = [
                (radius + arrow_length * math.cos(rad_angle),
                 radius + arrow_length * math.sin(rad_angle)),
                (radius + 10 * math.cos(rad_angle + math.radians(150)),
                 radius + 10 * math.sin(rad_angle + math.radians(150))),
                (radius + 10 * math.cos(rad_angle - math.radians(150)),
                 radius + 10 * math.sin(rad_angle - math.radians(150)))
            ]
            pygame.draw.polygon(container, COLORS["white"], arrow_points)

            text = font.render(f"{vs:+.1f}", True, COL-ORS["white"])
            text_rect = text.get_rect(center=(radius, radius + 40))
            container.blit(text, text_rect)
            surface.blit(container, (x, y))
params = [True] * 10
roll = math.radians(10)
pitch = math.radians(-5)
yaw = math.radians(90)
airspeed = 150
vs = 1
altitude = 350
fuel_level = 73
engine_rpm = 2000
temp = 19
t_eng = 690
oil = 9
def draw_altimeter(surface, altitude, x, y, size):
    radius = size // 2
    border_width = 5
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 16)
    max_altitude = 2000

    container = pygame.Surface((size, size), pygame.SRCALPHA)

    pygame.draw.circle(container, COLORS["white"], (radius, radius), radius, border_width)

    pygame.draw.circle(container, COLORS["black"], (radius, radius), radius - border_width)

    label_text1 = small_font.render("ВЫСОТА", True, COL-ORS["yellow"])
    label_rect1 = label_text1.get_rect(topright=(size - 75, 55))
    container.blit(label_text1, label_rect1)

    label_text = small_font.render("х100 М", True, COL-ORS["white"])
    label_rect = label_text.get_rect(topright=(size - 83, 75))
    container.blit(label_text, label_rect)

    for angle in range(-90, 271, 36):
        rad_angle = math.radians(angle)
        start = (radius + (radius - border_width) * math.cos(rad_angle),
                 radius + (radius - border_width) * math.sin(rad_angle))
        end = (radius + (radius - border_width - 15) * math.cos(rad_angle),
               radius + (radius - border_width - 15) * math.sin(rad_angle))
        pygame.draw.line(container, COLORS["white"], start, end, 2)

    start_angle = -90
    scale_range = 360

    for alt_mark in range(0, max_altitude + 1, 100):
        angle = start_angle - (alt_mark / max_altitude) * scale_range
        rad_angle = math.radians(angle)

        if alt_mark % 200 == 0:
            length = 15
            text = font.render(str(alt_mark // 100), True, COLORS["white"])
            text_rect = text.get_rect(
                center=(radius + (radius - 35) * math.cos(rad_angle),
                        radius + (radius - 35) * math.sin(rad_angle)))
            container.blit(text, text_rect)
        else:
            length = 8

            start = (radius + (radius - border_width) * math.cos(rad_angle),
                     radius + (radius - border_width) * math.sin(rad_angle))
            end = (radius + (radius - border_width - length) * math.cos(rad_angle),
                   radius + (radius - border_width - length) * math.sin(rad_angle))
            pygame.draw.line(container, COLORS["white"], start, end, 2)

            arrow_angle = start_angle - (altitude / max_altitude) * scale_range
            rad_angle = math.radians(arrow_angle)

            arrow_length = radius - 25
            arrow_points = [
                (radius + arrow_length * math.cos(rad_angle),
                 radius + arrow_length * math.sin(rad_angle)),
                (radius + 10 * math.cos(rad_angle + math.radians(150)),
                 radius + 10 * math.sin(rad_angle + math.radians(150))),
                (radius + 10 * math.cos(rad_angle - math.radians(150)),
                 radius + 10 * math.sin(rad_angle - math.radians(150)))
            ]
            pygame.draw.polygon(container, COLORS["white"], arrow_points)

            text = font.render(f"{int(altitude)}", True, COL-ORS["white"])
            text_rect = text.get_rect(center=(radius, radius + 30))
            container.blit(text, text_rect)

            surface.blit(container, (x, y))


def draw_fuel_indicator(surface, fuel, x, y, width, height):
    font = pygame.font.Font(None, 30)
    border_width = 4

    container = pygame.Surface((width, height), pygame.SRCALPHA)

    pygame.draw.rect(container, COLORS["black"], (0, 0, width, height))

    pygame.draw.line(container, COLORS["black"], (0, 0), (width, 0), border_width)
    pygame.draw.line(container, COLORS["black"], (0, 0), (0, height), border_width)
    pygame.draw.line(container, COLORS["white"], (width, 0), (width, height), border_width)
    pygame.draw.line(container, COLORS["white"], (0, height), (width, height), border_width)

    label_text = font.render("заряд", True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2, height // 2 - 15))
    container.blit(label_text, label_rect)

    fuel_text = font.render(f"{fuel}%", True, COLORS["white"])
    fuel_rect = fuel_text.get_rect(center=(width // 2, height // 2 + 8))
    container.blit(fuel_text, fuel_rect)

    surface.blit(container, (x, y))

def draw_clock(surface, x, y, width, height):
    font = pygame.font.Font(None, 24)
    clock_font = pygame.font.Font(None, 30)
    border_width = 4

    container = pygame.Surface((width, height), pygame.SRCALPHA)

    pygame.draw.rect(container, COLORS["black"], (0, 0, width, height))

    pygame.draw.line(container, COLORS["black"], (0, 0), (width, 0), border_width)
    pygame.draw.line(container, COLORS["black"], (0, 0), (0, height), border_width)
    pygame.draw.line(container, COLORS["white"], (width, 0), (width, height), border_width)
    pygame.draw.line(container, COLORS["white"], (0, height), (width, height), border_width)

    label_text = font.render("время", True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2, 10))
    container.blit(label_text, label_rect)

    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    clock_text = clock_font.render(current_time, True, COL-ORS["white"])
    clock_rect = clock_text.get_rect(center=(width // 2, height // 1.8))
    container.blit(clock_text, clock_rect)

    surface.blit(container, (x, y))

def draw_rpm_indicator(surface, rpm, x, y, width, height):
    font = pygame.font.Font(None, 24)
    rpm_font = pygame.font.Font(None, 30)
    border_width = 3

    container = pygame.Surface((width, height), pygame.SRCALPHA)

    pygame.draw.rect(container, COLORS["black"], (0, 0, width, height))

    pygame.draw.line(container, COLORS["black"], (0, 0), (width, 0), border_width)
    pygame.draw.line(container, COLORS["black"], (0, 0), (0, height), border_width)
    pygame.draw.line(container, COLORS["white"], (width, 0), (width, height), border_width)
    pygame.draw.line(container, COLORS["white"], (0, height), (width, height), border_width)

    label_text = font.render("об/мин", True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2, 15))
    container.blit(label_text, label_rect)

    rpm_text = rpm_font.render(f"{rpm}", True, COL-ORS["white"])
    rpm_rect = rpm_text.get_rect(center=(width // 2, height // 2 + 8))
    container.blit(rpm_text, rpm_rect)

    surface.blit(container, (x, y))

def draw_temperature(surface, temp, x, y, width, height):
    font = pygame.font.Font(None, 24)
    rpm_font = pygame.font.Font(None, 30)
    border_width = 3

    container = pygame.Surface((width, height), pygame.SRCALPHA)

    pygame.draw.rect(container, COLORS["black"], (0, 0, width, height))

    pygame.draw.line(container, COLORS["black"], (0, 0), (width, 0), border_width)
    pygame.draw.line(container, COLORS["black"], (0, 0), (0, height), border_width)
    pygame.draw.line(container, COLORS["white"], (width, 0), (width, height), border_width)
    pygame.draw.line(container, COLORS["white"], (0, height), (width, height), border_width)

    label_text = font.render("темп-ра", True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2, 10))
    container.blit(label_text, label_rect)

    label_text = font.render("за бортом", True, COL-ORS["white"])
    label_rect = label_text.get_rect(center=(width // 2, 25))
    container.blit(label_text, label_rect)

    rpm_text = rpm_font.render(f"{temp}", True, COL-ORS["white"])
    rpm_rect = rpm_text.get_rect(center=(width // 2 - 10, height // 2 + 13))
    container.blit(rpm_text, rpm_rect)

    label_text = font.render("C", True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2 + 17, height // 2 + 13))
    container.blit(label_text, label_rect)

    label_text = font.render(chr(176), True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2 + 9, height // 2 + 13))
    container.blit(label_text, label_rect)

    surface.blit(container, (x, y))

def draw_temp_engine(surface, t_eng, x, y, width, height):
    font = pygame.font.Font(None, 24)
    rpm_font = pygame.font.Font(None, 30)
    border_width = 3

    container = pygame.Surface((width, height), pygame.SRCALPHA)

    pygame.draw.rect(container, COLORS["black"], (0, 0, width, height))

    pygame.draw.line(container, COLORS["black"], (0, 0), (width, 0), border_width)
    pygame.draw.line(container, COLORS["black"], (0, 0), (0, height), border_width)
    pygame.draw.line(container, COLORS["white"], (width, 0), (width, height), border_width)
    pygame.draw.line(container, COLORS["white"], (0, height), (width, height), border_width)

    label_text = font.render("темп-ра", True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2, 10))
    container.blit(label_text, label_rect)

    label_text = font.render("двигателя", True, COL-ORS["white"])
    label_rect = label_text.get_rect(center=(width // 2, 25))
    container.blit(label_text, label_rect)

    rpm_text = rpm_font.render(f"{t_eng}", True, COL-ORS["white"])
    rpm_rect = rpm_text.get_rect(center=(width // 2 - 10, height // 2 + 13))
    container.blit(rpm_text, rpm_rect)

    label_text = font.render("C", True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2 + 19, height // 2 + 13))
    container.blit(label_text, label_rect)

    label_text = font.render(chr(176), True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2 + 11, height // 2 + 13))
    container.blit(label_text, label_rect)

    surface.blit(container, (x, y))

def draw_oil(surface, oil, x, y, width, height):
    font = pygame.font.Font(None, 24)
    rpm_font = pygame.font.Font(None, 30)
    border_width = 3

    container = pygame.Surface((width, height), pygame.SRCALPHA)

    pygame.draw.rect(container, COLORS["black"], (0, 0, width, height))

    pygame.draw.line(container, COLORS["black"], (0, 0), (width, 0), border_width)
    pygame.draw.line(container, COLORS["black"], (0, 0), (0, height), border_width)
    pygame.draw.line(container, COLORS["white"], (width, 0), (width, height), border_width)
    pygame.draw.line(container, COLORS["white"], (0, height), (width, height), border_width)

    label_text = font.render("кол-во", True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2, 10))
    container.blit(label_text, label_rect)

    label_text = font.render("масла", True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2, 25))
    container.blit(label_text, label_rect)

    rpm_text = rpm_font.render(f"{oil}", True, COL-ORS["white"])
    rpm_rect = rpm_text.get_rect(center=(width // 2 - 10, height // 2 + 13))
    container.blit(rpm_text, rpm_rect)

    label_text = font.render("Л", True, COLORS["white"])
    label_rect = label_text.get_rect(center=(width // 2 + 8, height // 2 + 13))
    container.blit(label_text, label_rect)

    surface.blit(container, (x, y))

def get_top_sensors_data():
  return [
      {"name": "Потеря связи", "abbreviation": "ПС", "value": False},
      {"name": "Низкий заряд", "abbreviation": "НЗ", "value": False},
      {"name": "Ошибка двигателя", "abbreviation": "ОД", "val-ue": False},
      {"name": "Ошибка датчика", "abbreviation": "ОДТ", "val-ue": False},
      {"name": "Потеря ориентации", "abbreviation": "ПО", "value": False},
      {"name": "Ошибка стабилизации", "abbreviation": "ОС", "value": False},
      {"name": "Перегрев", "abbreviation": "ПГ", "value": False},
      {"name": "Сильная вибрация", "abbreviation": "СВ", "val-ue": False},
      {"name": "Нет сигнала GPS", "abbreviation": "GPS", "val-ue": False},
      {"name": "Ошибка высоты", "abbreviation": "ОВ", "value": False},
  ]

font = pygame.font.Font(None, 24)
if __name__ == '__main__':
    gui_conn = GuiConnection()
    gui_event_pipe = gui_conn.connect_rx('localhost', 5505, gui_callback)
    gui_conn.start()
    telnet_conn = TelnetConnection('localhost', 5500)
    telnet_conn.connect()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        speed = telnet_conn.get_prop('/velocities/airspeed-kt')
        pipe_data = gui_event_pipe.parent_recv()
        lat_deg, lon_deg, alt_m, agl_m, phi_rad, theta_rad, psi_rad, climb_rate = 	pipe_data
        screen.fill(COLORS["background"])
        sensor_data = get_top_sensors_data()
        draw_top_sensors(screen, sensor_data)
        draw_attitude_indicator(screen, math.radians(phi_rad), math.radians(theta_rad), 450, 100, 300)
        draw_heading_indicator(screen, math.radians(psi_rad), 500, 450, 200)
        draw_speed_indicator(screen, speed, 150, 155, 200)
        draw_vsi_indicator(screen, climb_rate / 3.281, 750, 400, 200)
        draw_altimeter(screen, alt_m, 250, 400, 200)
        draw_fuel_indicator(screen, fuel_level, 800, 180, 100, 60)
        draw_clock(screen, 800, 100, 100, 60)
        draw_rpm_indicator(screen, engine_rpm, 800, 260, 100, 60)
        draw_temperature(screen, temp, 940, 100, 100, 60)
        draw_temp_engine(screen, t_eng, 940, 180, 100, 60)
        draw_oil(screen, oil, 940, 260, 100, 60)
        pygame.display.flip()
        clock.tick(30)
        latitude = 54.524580
        longitude = 39.701148
        m = folium.Map(location=[latitude, longitude], zoom_start=15)
        arrow_icon_url = "https://cdn-icons-png.flaticon.com/128/635/635717.png"
        arrow_icon = CustomIcon(
    icon_image=arrow_icon_url,
    icon_size=(40, 40),
    icon_anchor=(20, 20),
        )
        folium.Marker(
    location=[latitude, longitude],
    popup="Начальная точка",
    icon=arrow_icon,
        ).add_to(m)
        line_points = [
    [latitude, longitude],
    [latitude - 0.01, longitude + 0.01],
    [latitude + 0.01, longitude - 0.01],
    [latitude + 0.02, longitude - 0.01],
        ]
        folium.PolyLine(
    locations=line_points,
    color="blue",
    weight=3,
    opacity=0.8,
        ).add_to(m)
        for point in line_points:
            folium.CircleMarker(
        location=point,
        radius=3,
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=1.0,
        popup=f"Точка: {point}",
            ).add_to(m)
        m.save("helicopter_path_with_dots.html")
        import webbrowser
        webbrowser.open("helicopter_path_with_dots.html")
    pygame.quit()
