import os
import sys
import pygame

# Pastikan direktori root masuk ke sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.scenes.main_menu import MainMenuScene
from src.scenes.song_select_scene import SongSelectScene
from src.scenes.game_scene import GameScene
from src.scenes.visualizer_scene import VisualizerScene
from src.scenes.settings_scene import SettingsScene


def main():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Piano Master Classic & Visualizer")
    clock = pygame.time.Clock()

    current_scene_name = "main_menu"
    selected_midi_path = None

    while current_scene_name != "quit":
        if current_scene_name == "main_menu":
            scene = MainMenuScene(screen, clock)
            current_scene_name = scene.run()
        elif current_scene_name == "song_select":
            scene = SongSelectScene(screen, clock)
            result = scene.run()
            if result in ("quit", "main_menu"):
                current_scene_name = result
            else:
                # result adalah path berkas MIDI yang dipilih
                selected_midi_path = result
                current_scene_name = "game"
        elif current_scene_name == "game":
            scene = GameScene(screen, clock, midi_path=selected_midi_path)
            current_scene_name = scene.run()
        elif current_scene_name == "visualizer":
            scene = VisualizerScene(screen, clock)
            current_scene_name = scene.run()
        elif current_scene_name == "settings":
            scene = SettingsScene(screen, clock)
            current_scene_name = scene.run()
        else:
            break

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
