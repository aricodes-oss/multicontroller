import os
import pygame
import serial

from .state import ControllerState

# Run pygame headless
os.putenv("SDL_VIDEODRIVER", "dummy")

pygame.init()
pygame.joystick.init()

clock = pygame.time.Clock()


def main():
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    running = True

    state = ControllerState()
    ser = serial.Serial("/dev/ttyUSB0", 115200)

    while running:
        for event in pygame.event.get():
            state.update(event)

        ser.write(state.report + b"\n")
        clock.tick(5000)


if __name__ == "__main__":
    main()
