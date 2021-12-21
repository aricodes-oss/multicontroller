from math import floor

from pygame.event import Event
from pygame.locals import JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION, JOYAXISMOTION

from .mapping import BUTTONS, BUTTONS_TO_BYTE

STICK_AXIS_SCALE = 32766


def _normalize_trigger(val: float) -> int:
    effective = val

    if val < -1:
        effective = -1

    if val > 1:
        effective = 1

    return floor((effective + 1) * (255 / 2))


def _normalize_range(val: float) -> int:
    if val < -2:
        # This seems to only happen when resetting to netural?
        return 0

    if val < -1:
        return -STICK_AXIS_SCALE

    if val > 1:
        return STICK_AXIS_SCALE

    res = val * STICK_AXIS_SCALE

    # Python lacks a proper "round towards 0" function
    # so here we are
    if res > -1 and res < 0:
        return 0

    return floor(res)


def _normalize_axis(axis: int) -> int:
    # For some reason LSTICK is axes [0, 1] and RSTICK is axes [3, 4]
    # LTRIGGER/RTRIGGER are [2, 5] respectively, which... why
    return [0, 1, 4, 2, 3, 5][axis]


def _set_bit(field, bit, val):
    if val:
        return field | 1 << bit

    return field & ~(1 << bit)


class ControllerState:
    _buttons: list[int] = list([0] * 11)
    _hat: list[int] = list([0] * 2)
    _sticks: list[int] = list([0] * 4)
    _triggers: list[int] = list([0] * 2)
    _report: bytearray = bytearray(12)

    def update(self, e: Event):
        if e.type == JOYBUTTONDOWN:
            self.press_button(e.button)
        if e.type == JOYBUTTONUP:
            self.release_button(e.button)

        if e.type == JOYAXISMOTION:
            self.move_stick(e.axis, e.value)

        if e.type == JOYHATMOTION:
            self.move_hat(e.value)

    def press_button(self, code: int):
        self._buttons[code] = True

    def release_button(self, code: int):
        self._buttons[code] = False

    def move_hat(self, hat_val: list[int]):
        self._hat = hat_val

    def set_trigger(self, axis: int, val: float):
        naxis = _normalize_axis(axis) - 4

        self._triggers[naxis] = _normalize_trigger(val)

    def move_stick(self, axis: int, val: float):
        naxis = _normalize_axis(axis)

        if naxis >= 4:
            return self.set_trigger(axis, val)

        self._sticks[naxis] = _normalize_range(val)

    def _pack_hat(self, r: bytearray):
        # U/D/L/R
        r[0] = _set_bit(r[0], 0, self._hat[1] == 1)
        r[0] = _set_bit(r[0], 1, self._hat[1] == -1)

        r[0] = _set_bit(r[0], 2, self._hat[0] == -1)
        r[0] = _set_bit(r[0], 3, self._hat[0] == 1)

    def _pack_buttons(self, r: bytearray):
        for idx, val in enumerate(self._buttons):
            byte_num = BUTTONS_TO_BYTE[idx]

            r[byte_num] = _set_bit(r[byte_num], BUTTONS[idx], val)

    def _pack_triggers(self, r: bytearray):
        r[2] = self._triggers[0]
        r[3] = self._triggers[1]

    def _pack_sticks(self, r: bytearray):
        def _tb(val):
            return val.to_bytes(2, byteorder="little", signed=True)

        lbytes = _tb(self._sticks[0]) + _tb(self._sticks[1])
        rbytes = _tb(self._sticks[2]) + _tb(self._sticks[3])

        r[4], r[5], r[6], r[7] = lbytes
        r[8], r[9], r[10], r[11] = rbytes

    @property
    def report(self):
        # This whole "aliasing self._report" thing is to just save me some typing
        # while bit twiddling, which is already tedious
        r = self._report

        self._pack_hat(r)
        self._pack_buttons(r)
        self._pack_triggers(r)
        self._pack_sticks(r)

        return self._report
