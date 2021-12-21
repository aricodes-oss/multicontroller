# multicontroller

Uses [`pygame`](https://www.pygame.org/) to convert controller signals to `xinput` byte strings and send them over `uart` to a [pico microcontroller](https://www.raspberrypi.com/products/raspberry-pi-pico/) wherein they will be dispatched to a console via the [USB HID spec](https://www.partsnotincluded.com/understanding-the-xbox-360-wired-controllers-usb-data/).

Basically, this exists so we can take 2 controllers in and output one.

This lets us do a couple things:

- Only send a button press if both controllers are pushing that button ("one mind" mode)
- Randomly swap which controller controls the output ("chaos" mode)
- Delegate which controller is allowed to press what buttons ("2P1C" mode)
- Add about a millisecond of input delay ("microcontroller processing isn't free" mode)

# Contributing

Please.
