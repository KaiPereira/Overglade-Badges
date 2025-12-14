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

Finally, we have the NFC tag:

![[Pasted image 20251214125752.png]]

The IC is called the tag, and then the inductor symbol is where the antenna is. It works passively by harvesting the energy from the magnetic fields on your phone, but I decided to also implement active NFC so I wired the I2C and the other control pins so that people can customize it even further.

You'll notice the load cap on the antenna, this is the same one as the crystal to minimize the BOM, and it's for frequency tuning, so it smooths the capacitance of the antenna for impedance matching. 

And just like that, we have our entire schematic!

![[Pasted image 20251214130033.png]]

Now, let's get onto the PCB!

![[Pasted image 20251214130114.png]]

I'll just give a brief overview of the main logic, but essentially, it's in the shape of a ticket, which was a sticker I liked that Kai Ling made, so I wanted to follow that idea because I think it would be really cool.

The power traces are thick enough to drive 1A, and then USB is 90 ohm impedance matched. My routing probably could've been more clean, but it's fine for a quick board. 

The hole is very specific, and I designed it that way because the board will be right side heavy, so I wanted the clip to help balance that out, by hitting the angle of the hexagon and not sliding.

Next, let's talk about the NFC antenna. I used https://eds.st.com/antenna/#/ to generate an optimal antenna, which needed to be a target inductance of 4.7uH. I then used https://github.com/nideri/nfc_antenna_generator to create the actual footprint, and then I added my own via's to it, and I also decided on using an angled center to the NFC tag, so that I could put the IC directly centered under the antenna.

Finally, we have some of the cosmetic aspects of the PCB. I added exposed copper art by having soldermask designs around the PCB, and then the ground fill would go over that and make it look at coppery. Pretty fancy :D 

There's no ground fill under the NFC antenna, because I don't want it to dampen the antenna, and I am a bit worried because there's one surrounding it, but I think I'm just overthinking it. I also made a custom header footprint because I thought it looked really cool! 

And just like that, that's our PCB finished! 

I then generated all the production files using the KiCad fabrication toolkit plugin, and it's ready for JLC! There's a lot of stuff I didn't mention, but that's a general overview of the PCB!

