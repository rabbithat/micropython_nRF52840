# micropython_nRF52840

This is tested and working "proprietary" radio demo code. It shows simple transmit and receive radio functionality.

It is written entirely in micropython, and it works on both nRF52832 and nRF52840. In brief: the transmitter sends a packet with a different one-byte payload about once every second, and the receiver displays the content of the payload as well as an ongoing count of the number of packets received.

In this case "proprietary" simply means Nordic's proprietary radio mode. Anyone can use it. It's very similar to the frames sent by the nRF24L01+. It does not rely on bluetooth.

Load the code into a file named main.py. I used ampy to put the file onto the board (in my case I used an nRF52840-DK as the transmitter and an nRF52832-DK as the receiver). Then, reset the board, which loads the code. Then open a putty window (or similar serial terminal) to the board and type:
start()
at the ">>>" REPL prompt to execute the code. You could, of course, have it start itself, but then I found it difficult to regain control over the board if I did it that way (e.g. to upload a new program). This way you regain control by just resetting the board.

Presently the transmitter is sending packets faster than one a second, but for demo purposes that doesn't matter. The receiver has no problem keeping up with it.

With this as a starting point, you can easily extend the code to do whatever you want.

Note: you will need to fix the micropython machine module as explained here by dhylands: viewtopic.php?f=12&t=5377
to get the code to work.


