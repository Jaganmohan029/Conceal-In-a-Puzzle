# Conceal-In-a-Puzzle
Hide your message in a SUDOKU puzzle

In our project we used Optical Character Recognition mechanism to extract the image from the user which contains an unsolved o partially filled SUDOKU which is a logic based, combinatorial number-placement puzzle. The objective is to fill a 9×9 grid with digits so that each column, each row, and each of the nine 3×3 sub-grids that compose the grid also called "boxes", "blocks", "regions", or "sub-squares" contains all of the digits from 1 to 9. The puzzle setter provides a partially completed grid, which for a well-posed puzzle has a unique solution. After extracting the unsolved Sudoku image we incorporated Knuth’s algorithm or the Dancing links algorithm to solve the Sudoku puzzle. Then using our own algorithm we embed the user’s data or a message into the Sudoku blanks without disrupting the rules of the puzzle.
 
The project basically has three phases:
       1. Extracting the image from the user with an unsolved Sudoku.
       2. Solving the Sudoku using Knuth’s algorithm.
       3. Embedding the data into the Sudoku and generating a key.
       

Proposed  System:
      The proposed model embeds the user’s data which contains characters such as A to Z and numbers like 0 to 9 and any others by their ASCII values into the solved Sudoku’s cells that had been solved by using the dancing links algorithm or Knuth’s algorithm and modify it for balancing the Sudoku. While doing so our algorithm generates a key with respect to the message or data given by the user and finally the sender will be left with a partially filled Sudoku just as the one given by him/her and be sent to the other end there, at the receiver’s end the reverse process will be done with the key and the message will be retrieved.

Limitations and Recomendations:
  1. The data from the user should be in image format with an unsolved Sudoku in it.
  2. The image should not be distorted because of the OCR limitations.
  3. The image should be in digital format.
  4. The data or the message can contain any character that contains ASCII value.
  5. The image from the user may not be uniformly scaled and hence should be done for effective extraction.
  6. The All the images are transformed from RGB to Gray scale images. 

Software requirements: 
    The following list includes the necessary software required for the operation of the system. It includes,
      * Python 2.7. (Execution)
      * Tesseract 0.9.
      * Numpy.
      * Tkinter. (User-Interface)
      * Opencv2. (OCR)
      * Pillow.
 
 Steps to Execute:
  Sender:
   * Run SenderSudoku.py and input an unsolved sudoku.
   * Click Solve.
   * Input the message and and select the desired "Encrypt On" button for embedding the user message.
   * Select the Index.
   * Click on Encrypt.
   * Send the Final Sudoku Image and the key to the other enduser (via some protected medium).
  Receiver:
   * Run ReceiverSudoku.py and input the Final Sudoku Image.
   * Click Solve.
   * Click Decrypt once the Sudoku is read and solved.
   * Message decrypted.
   
 Please see the sample screenshots included in the repo for deeper understanding.
