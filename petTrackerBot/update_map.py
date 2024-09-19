import time
from pathlib import Path

import folium
import random

from petTrackerBot.constants.paths import paths
from petTrackerBot.petTrackerApp.tables import DBMapInfo
from petTrackerBot.utils.WebDriverLinux import WebDriverLinux


def generate_random_coordinates():
    # Задаем границы для баренцева моря
    latitude = random.uniform(70.0, 74.0)  # Широта
    longitude = random.uniform(30.0, 50.0)  # Долгота
    return latitude, longitude


def create_map(latitude, longitude, save_path: Path):
    # Создаем объект карты с центром в указанных координатах
    m = folium.Map(location=[latitude, longitude], zoom_start=4)

    # Добавляем маркер на карту
    folium.Marker(
        location=[latitude, longitude],
        popup=f'Координаты: ({latitude:.4f}, {longitude:.4f})',
        icon=folium.Icon(color='red')
    ).add_to(m)

    # Сохраняем карту в HTML файл
    m.save(save_path)


def get_html_as_png(html_path: Path) -> Path:
    png_path = html_path.with_name('map_png.png')
    with WebDriverLinux() as driver:
        driver.get(f"file:///{html_path}")
        time.sleep(5)
        driver.get_screenshot_as_file(png_path)
    return png_path


async def update_map():
    coordinates = generate_random_coordinates()
    new_map_path = paths.get_new_db_files_folder() / 'map.html'
    create_map(*coordinates, save_path=new_map_path)

    map_png_path = get_html_as_png(new_map_path)

    await DBMapInfo.insert(
        DBMapInfo(
            image_path=str(map_png_path),
            information=f'Coordinates: {coordinates}'
        )
    )
