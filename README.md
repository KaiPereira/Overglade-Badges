# Overglade Hackathon Badges

<img width="2560" height="1407" alt="image" src="https://github.com/user-attachments/assets/6994a2e5-22f4-446f-9456-5f8738ce2202" />

<img width="2560" height="1407" alt="image" src="https://github.com/user-attachments/assets/a625fa2b-5c37-43a8-b935-c30a519a3aa5" />


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

<img width="2560" height="1405" alt="image" src="https://github.com/user-attachments/assets/5806ac54-13aa-48d3-b724-f143bebe1431" />

## Programming

The board is going to have an embedded programmer and also a web interface for programming. This just functions as a backup so that you can always program the board properly!

The code is accessible in the [/programming](/programming) folder! I stole this from [@mpkendall](https://github.com/mpkendall), but we might make a custom version too! 
