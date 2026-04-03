# Overglade Hackathon Badges

These are zero-power hackathon badges I designed for a hackathon in singapore! They're powered by the RP2040 and have passive NFC and an onboard e-ink driver! 

<img width="1333" height="1000" alt="image 3" src="https://github.com/user-attachments/assets/31bc2249-8f35-4ed4-b9d6-c4fc2e519038" />

<img width="1333" height="1000" alt="image 2" src="https://github.com/user-attachments/assets/47a4892c-bcd6-4e2c-aa83-acc790376328" />


## Custom Features
- Passive NFC tap for whatever your heart desires
- E-ink support so that you don't need any battery
- 20 GPIO's broken out onto header pins for programming
- Active NFC mode if you want to do some more complicated stuff
- Zero power, the board needs no power for it's core features
- RP2040 SoC with 4MB flash memory
- Cool PCB and exposed copper art

## PCB Design

The PCB is a simple, 2 layer board with ground fills on each layer. I also CAD'ed the shapes and art of the board to make sure everything was perfectly symmetrical!

<img width="2560" height="1405" alt="image" src="https://github.com/user-attachments/assets/734cdccf-5653-47d2-85f2-d92385ca3819" />

<img width="2560" height="1405" alt="image" src="https://github.com/user-attachments/assets/5806ac54-13aa-48d3-b724-f143bebe1431" />

## Programming and Setup

The board is really easy to setup! Just plug it into your computer via USB-C, drop in the [Pi Pico micropython bootloader](https://micropython.org/download/RPI_PICO2/) and then upload the code using Thonny to the devboard! 

You can modify the `config.json` to add your own personal details, and change the images by replacing the bitmaps (I like to use [Magick](https://imagemagick.org/#gsc.tab=0) for this)!

