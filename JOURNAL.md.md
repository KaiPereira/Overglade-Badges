---
title: Overglade PCB's
author: Kai Pereira
description: NFC hackathon badges for the Overglade game jam in Singapore!
created_at: 2025-12-14
---
## Let's get into it

This is a retroactive journal of how I made the Overglade PCB's, I absolutely locked in and made these really quick, so I didn't want the overhead of actively journaling it.

The first part of the PCB is the power.

![[Pasted image 20251214124754.png]]

I decided to use USB-C because it's the most common cable these days and has really good power, and data. I use the NCP1117 fixed LDO to power 3V3 because it's very good, and can step down 1A which is the max draw of my board.

I added ESD protection because lots of people are writing and messing with their badges, so I don't want to accidentally fry the PCB.

The next part of the PCB is the MCU. I decided on RP2040, because it's insanely easy to program, cheap and is just really fast to get working!

![[Pasted image 20251214124941.png]]

This is a really simple RP2040 implementation. It's just one cap per VDD pin, and then a bulk cap for each line.

I added a power LED to show that power is actually getting to the board, and a BOOT and RESET button for programming. There's an external crystal for the USB-C timing, and then I strategically wired the GPIO's for the easiest routing to the pin headers.

![[Pasted image 20251214125103.png]]

The pin headers is near standard with the RP2040, but it is smaller. I didn't put too much thought into it, but just wanted to break out everything to be accessible and useful to the user.

Next, I needed to have an e-ink on the board.

![[Pasted image 20251214125147.png]]
This PCB should work with absolutely no power, so that's why I decided on an e-ink because it's a passive display and doesn't actively need power. I copied the waveshare reference schematic for this part, but I understand the e-ink at a fair level.

There's decoupling on all the lines that are driving power to the e-ink:
- Pre-VGH is the previous high voltage which is important to move the charged particles in the e-ink
- Pre-VGL is the previous gate low which is also a key aspect of moving the particles, and these 2 together are basically moving in sync to make the particles move quickly and efficiently. 

It's driven by SPI, and has resistor selection for different displays, and also a gate drive control which drives it on and off to actively change the display.

There's an inductor to help with the internal DC-DC boost converter inside of the e-ink and decoupling for it too.
