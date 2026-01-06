# Overglade Hackathon Badges

<img width="1904" height="1095" alt="image" src="https://github.com/user-attachments/assets/3af2cdbc-e8b5-470a-a43d-b1a9fe20f0e1" />

These are the (UNFINISHED) hackathon badges for Hackclub Overglade, a game jam within a game that's going to be happening in Singapore! They function as devboards, but also as badges with NFC tap, and e-inks!

## Custom Features
- Passive NFC tap for whatever your heart desires
- E-ink support so that you don't need any battery
- 20 GPIO's broken out onto header pins for programming
- Active NFC mode if you want to do some more complicated stuff
- Zero power, the board needs no power for it's core features
- RP2040 SoC with 4MB flash memory
- Cool PCB and exposed copper art (TBD)

## PCB Design

The PCB is a simple, 2 layer board with ground fills on each layer. I also CAD'ed the shapes and art of the board to make sure everything was perfectly symmetrical!

<img width="2560" height="1405" alt="image" src="https://github.com/user-attachments/assets/734cdccf-5653-47d2-85f2-d92385ca3819" />

<img width="2560" height="1402" alt="image" src="https://github.com/user-attachments/assets/7781f4f4-66ac-485d-ba02-8e33d7d32074" />

## Programming

The board is going to have an embedded programmer and also a web interface for programming. This just functions as a backup so that you can always program the board properly!

The code is accessible in the [/programming](/programming) folder! I stole this from [@mpkendall](https://github.com/mpkendall), but we might make a custom version too! 
