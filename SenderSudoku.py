from Tkinter import *
import time
import cv2
import numpy as np
import sys
import tesseract
import solve
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
API = tesseract.TessBaseAPI()
def complete_save(sv_sudoku):
    img = Image.open("blanksudoku.jpg")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("micross.ttf", 25)
    x=30
    y=30
    print sv_sudoku
    for i in range(1,10):
        for j in range(1,10):
            if(sv_sudoku[i-1][j-1]=='x'):
                m=0
            else:
                draw.text((x, y),str(sv_sudoku[i-1][j-1]),(0,0,0),font=font)
            x=x+55
        y=y+55
        x=30
    img.save('sampleout.jpg')

    
def get_value(str):
    i=0
    print str
    if str.isdigit():
        i=1
    else:
        i=2
    k=i
    count=0
    if(i==1):
        for j in range(len(str)):
            k=k*10+int(str[j])
    elif(i==2):
        for j in range(len(str)):
            f=ord(str[j])
            if(f==32):
                f=96
            k=k*100+(f-23)
    else:
        for j in range(len(str)):
            try:
                z=int(str[j])
                k=k*10+z
                count=count+1
            except:
                f=0
        for j in range(len(str)):
            if(ord(str[j])>47 and ord(str[j])<58):
                f=0
            else:
                k=k*10+(j)
                k=k*100+(ord(str[j])-23)
        print k
        k=k*10+count      
    return k
def solve_sudoku(RESULT):
    Set, keys, values = solve.sudo2set(RESULT)
    matrix = {}
    for i in xrange(len(keys)):
        key = keys[i]
        matrix[key]=[]
        for value in values:
            if value in Set[key]:
                matrix[key].append(1)
            else:
                matrix[key].append(0)    

    solutions = solve.exactcover(matrix)

    sudostring = ""
    for i in sorted(solutions[0]):
        sudostring += str(i[2]) + " "

    solved_sudoku = [sudostring[i:i+18] for i in xrange(0, 81*2, 18)]
    return solved_sudoku

def ocr_singledigit(image):
    API.Init(".", "eng", tesseract.OEM_DEFAULT)
    API.SetVariable("tessedit_char_whitelist", "123456789")
    API.SetPageSegMode(6)
    tesseract.SetCvImage(image, API)
    CHAR = API.GetUTF8Text()
    CHAR = CHAR.replace(" ", "").strip()
    
    if len(CHAR) == 0:
        return "x"
    return int(CHAR)
    
def split_len(item, length):
    return [item[i:i+length] for i in range(0, len(item), length)]

def getcorners(C, points):
    x = C[0]
    y = C[1]
    top_left_corner_index = 10 * y + x
    down_right_corner_index = top_left_corner_index + 11
    
    top_left_corner = points[top_left_corner_index]
    down_right_corner = points[down_right_corner_index]

    return (top_left_corner[0], down_right_corner[0], top_left_corner[1], down_right_corner[1])

def OCR(FileImage):

    print "file: " + FileImage
    print "Extracting Image"


    Image = cv2.imread(FileImage)
    Image = cv2.GaussianBlur(Image, (5, 5), 0)
    b_w = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
    Grid = np.zeros((b_w.shape), np.uint8)
    Grid_h = np.zeros((b_w.shape), np.uint8)
    Grid_v = np.zeros((b_w.shape), np.uint8)
    Structure = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    Clean = cv2.morphologyEx(b_w, cv2.MORPH_CLOSE, Structure)
    val = np.float32(b_w)/(Clean)
    r1 = np.uint8(cv2.normalize(val, val, 0, 255, cv2.NORM_MINMAX))
    r2 = cv2.adaptiveThreshold(r1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 0, 151, 70)
    

    Amp = cv2.adaptiveThreshold(r1, 255, 0, 1, 19, 2)

    Reg, Ht = cv2.findContours(Amp, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    MAX_AREA = 0
    for CNT in Reg:
        AREA = cv2.contourArea(CNT)
        if AREA > 1000 and AREA > MAX_AREA:
            MAX_AREA = AREA
            BEST_CNT = CNT
    cv2.drawContours(Grid, [BEST_CNT], 0, 255, -1)
   
    cv2.drawContours(Grid, [BEST_CNT], 0, 0, 2)
    r1 = cv2.bitwise_and(r1, Grid)
    
 
    KERNELX = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 10))

    DX = cv2.Sobel(r1, cv2.CV_64F, 1, 0)
    DX = cv2.convertScaleAbs(DX)
    cv2.normalize(DX, DX, 0, 255, cv2.NORM_MINMAX)
    RET, CLOSEX = cv2.threshold(DX, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    CLOSEX = cv2.morphologyEx(CLOSEX, cv2.MORPH_DILATE, KERNELX)
    CONTOUR, HIER = cv2.findContours(CLOSEX, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for CNT in CONTOUR:
        x, y, w, h = cv2.boundingRect(CNT)
        if h/w > 5:
            cv2.drawContours(CLOSEX, [CNT], 0, 255, -1)
        else:
            cv2.drawContours(CLOSEX, [CNT], 0, 0, -1)

    CLOSEX = cv2.morphologyEx(CLOSEX, cv2.MORPH_DILATE, None, iterations = 2)
    
    

    KERNELY = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 2))
    DY = cv2.Sobel(r1, cv2.CV_64F, 0, 1)
    DY = cv2.convertScaleAbs(DY)
    cv2.normalize(DY, DY, 0, 255, cv2.NORM_MINMAX)
    RET, CLOSEY = cv2.threshold(DY, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    CLOSEY = cv2.morphologyEx(CLOSEY, cv2.MORPH_DILATE, KERNELY)
    
    CONTOUR, HIER = cv2.findContours(CLOSEY, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for CNT in CONTOUR:
        x, y, w, h = cv2.boundingRect(CNT)
        if w/h > 5:
            cv2.drawContours(CLOSEY, [CNT], 0, 255, -1)
        else:
            cv2.drawContours(CLOSEY, [CNT], 0, 0, -1)

    CLOSEY = cv2.morphologyEx(CLOSEY, cv2.MORPH_DILATE, None, iterations = 2)
    r1 = cv2.bitwise_and(CLOSEX, CLOSEY)


    CONTOUR, HIER = cv2.findContours(r1, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    POINTS = []
    for CNT in CONTOUR:
        mom = cv2.moments(CNT)
        try:
            (x, y) = int(mom['m10']/mom['m00']), int(mom['m01']/mom['m00'])
            POINTS.append((x, y))
        except:
            print "wrong"
            POINTS.append((0,0))
    if len(POINTS) != 100:
        print "Centroids: " + str(len(POINTS))
        print "[!!!!]Exiting"
        sys.exit()
        

    C_POINTS = [sorted(i, key = lambda x: x[1]) for i in split_len(sorted(POINTS), 10)]

    R_POINTS = [ list(i) for i in zip(*C_POINTS)]
    R_POINTS = [x for sublist in R_POINTS for x in sublist]


    RESULT = [[0]*9 for i in range(9)]

    for row in range(9):
        for column in range(9):

            x1, x2, y1, y2 = getcorners((row, column), R_POINTS)

            crop = r2[y1 + 7 : y2 - 7 , x1 + 7: x2 - 7]

            digit = cv2.cv.CreateImageHeader((crop.shape[1], crop.shape[0]), cv2.cv.IPL_DEPTH_8U, 1)
            cv2.cv.SetData(digit, crop.tostring(), crop.dtype.itemsize*crop.shape[1])
            
        
            RESULT[column][row] = ocr_singledigit(digit)

    return RESULT


class App:
    def __init__(self, master,RESULT):
        frame = Frame(master)
        self.master=master
        frame.pack()
        self.sudoku=[]
        k=0
        l=0
        self.RESULT=RESULT
        self.button = Button(master,text="Solve", fg="black",command=self.load_sudoku)
        self.button.pack()
        for row in RESULT:
            string = ""
            for digit in row:
                string = str(digit)
                lk=Label(frame,text=string,width=3, fg="white",bg="grey",padx=3,pady=3)
                lk.grid(row=k,column=l)
                self.sudoku.append(lk)
                l=l+1
                if(l==9):
                    l=0
                    k=k+1
    def value(self,valueSudoku):
        count=0
        for k1 in range(9):
            c=valueSudoku[k1]
            d=[1,2,3,4,5,6,7,8,9]
            e=[]  
            n=9
            for i in range(9):
                k=c[i]
                j=d.index(k)
                e.append(j)
                d[j]=d[n-1]
                n=n-1
            n=1
            result=0
            for i in range(len(e)-1,-1,-1):
                result=result*n+e[i]
                n=n+1
            if(result<36287):
                count=count+1
        return count
    def identifyValue(self,valueSudoku):
            c=valueSudoku
            d=[1,2,3,4,5,6,7,8,9]
            e=[]  
            n=9
            for i in range(9):
                k=c[i]
                j=d.index(k)
                e.append(j)
                d[j]=d[n-1]
                n=n-1
            n=1
            result=0
            for i in range(len(e)-1,-1,-1):
                result=result*n+e[i]
                n=n+1
            return result
    def change(self,solvedSudoku):
        j=0
        k=0
        self.resultSudoku=[[0]*9 for i in range(9)]
        for i in solvedSudoku:
            j=0
            for i1 in i.split(): 
                self.resultSudoku[k][j]=int(i1)
                j=j+1
            k=k+1

    def display(self,solved_sudoku):
        k=0
        for i in solved_sudoku:
            for m in i.split():
                self.sudoku[k]['text']=m
                k=k+1
    def common_display(self,solved_sudoku):
        k=0
        for i in solved_sudoku:
            for m in i:
                self.sudoku[k]['text']=" "+str(m)
                k=k+1
    def encrypt_sudoku(self):
        text=self.T.get("1.0",'end-1c')
        if(text==""):
            start=0
            self.encryptSudoku=self.resultSudoku
            print "entered"
        else:
            enc_data=get_value(text)
            enc_text=str(enc_data)
            length=len(enc_text)
            print enc_data
            enc_rc=self.entry4.get()
            print enc_rc
            enc_index=self.variable.get()
            print enc_index
            index=int(enc_index)
            enc_irc=int(enc_rc)
            if(enc_irc==2):
                self.changeSudoku=[[0]*9 for i in range(9)]
                for i in range(9):
                    for j in range(9):
                        self.changeSudoku[i][j]=self.resultSudoku[j][i]
                self.resultSudoku1=self.changeSudoku
            if(enc_irc==1):
                self.resultSudoku1=self.resultSudoku
                        
            tk=length
            z=0
            l=0
            value=0
            indexes=[]
            start=0
            if(length<6):
                print "entered length"
                value=enc_data
                print value
                a=[1,2,3,4,5,6,7,8,9]
                b=value
                n=9
                result=0
                c=[]
                f=[]
                while(n):
                    i=b%n;
                    b=b/n;
                    f.append(i)
                    c.append(a[i])
                    a[i]=a[n-1]
                    n=n-1
                print c
                k=self.resultSudoku1[index]
                self.changeSudoku=[[0]*9 for i in range(9)]
                for i in range(9):
                    for j in range(9):
                        if(i==index):
                            self.changeSudoku[i][j]=c[j]
                        else:
                            self.changeSudoku[i][j]=c[k.index(self.resultSudoku1[i][j])]
                self.encryptSudoku=self.changeSudoku
                start=start+1
            else:
                while(length!=0):
                    if(z==0):
                        value=int(enc_data/(10**(length-6)))
                        if(value>362880):
                            value=value/10
                            length=length-5
                        else:
                            length=length-6
                        print value
                        indexes.append(index)
                        z=z+1
                        index=(index+1)%9
                    else:
                        length=length-1
                        indexes.append(index)
                        index=(index+1)%9
                    print indexes
                    length=tk
                    start=0
                    for index1 in indexes:
                        if(start==0):
                            value=int(enc_data/(10**(length-6)))
                            if(value>362880):
                                value=value/10
                                length=length-5
                                l=5
                            else:
                                 length=length-6
                                 l=6
                            print value
                            a=[1,2,3,4,5,6,7,8,9]
                            b=value
                            n=9
                            result=0
                            c=[]
                            f=[]
                            while(n):
                                i=b%n;
                                b=b/n;
                                f.append(i)
                                c.append(a[i])
                                a[i]=a[n-1]
                                n=n-1
                            print c
                            k=self.resultSudoku1[index1]
                            print k
                            self.changeSudoku=[[0]*9 for i in range(9)]
                            for i in range(9):
                                for j in range(9):
                                    if(i==index1):
                                        self.changeSudoku[i][j]=c[j]
                                    else:
                                        self.changeSudoku[i][j]=c[k.index(self.resultSudoku1[i][j])]
                            self.encryptSudoku=self.changeSudoku
                
                            start=start+1
                        else:
                            value1=int(enc_text[l])
                            print value
                            calcValue=self.identifyValue(self.encryptSudoku[index1])
                            print calcValue
                            flow_value=calcValue%10
                            calcValue=calcValue/10
                            calcValue=calcValue*10+value1
                            print calcValue
                            a=[1,2,3,4,5,6,7,8,9]
                            b=calcValue
                            n=9
                            result=0
                            c=[]
                            f=[]
                            while(n):
                                i=b%n;
                                b=b/n;
                                f.append(i)
                                c.append(a[i])
                                a[i]=a[n-1]
                                n=n-1
                            k=self.encryptSudoku[index1]
                            print k
                            self.changeSudoku=[[0]*9 for i in range(9)]
                            for i in range(9):
                                for j in range(9):
                                    if(i==index1):
                                        self.changeSudoku[i][j]=c[j]
                                    else:
                                        self.changeSudoku[i][j]=c[k.index(self.encryptSudoku[i][j])]
                            self.encryptSudoku=self.changeSudoku
                            length=length-1
                            start=start*10+flow_value
                            l=l+1
            start=start*10+int(enc_rc)
            print start
            start=start*10+int(enc_index)
            self.key=start
            if(enc_irc==2):
                self.changeSudoku=[[0]*9 for i in range(9)]
                for i in range(9):
                    for j in range(9):
                        self.changeSudoku[i][j]=self.encryptSudoku[j][i]
                self.encryptSudoku=self.changeSudoku
            self.common_display(self.encryptSudoku)
            for i in range(9):
                print self.encryptSudoku[i]
        if(self.decryptiter==0):
            self.decr=0
            frame4 = Frame(self.master)
            frame4.pack()
            self.l1=Label(frame4,text="Key Value:",width=10, fg='blue').grid(row=0,column=0)
            self.keyLabel=Label(frame4,text="",width=30, fg='blue')
            self.keyLabel.grid(row=0,column=1)
            self.keyLabel['text']=start
            self.button1 = Button(self.master,text="Save", fg="black",command=self.save_sudoku)
            self.button1.pack()
            self.decryptiter=self.decryptiter+1
        else:
            self.keyLabel['text']=start
        self.keyValue=start
        self.decryptSudoku=self.encryptSudoku
    def decryptMessage(self):
        st=str(self.decryptedValue)
        ty=int(self.decryptedValue/(10**((len(st)-1))))
        value=self.decryptedValue%(10**((len(st)-1)))
        print value
        msg=""
        print ty
        if(ty==1): 
            self.msgLabel['text']=value
        if(ty==2):
            while(value!=0):
                st=str(value)
                sol=int(value/(10**((len(st)-2))))
                value=value-sol*(10**((len(st)-2)))
                msg=msg+chr(sol+23)
            self.msgLabel['text']=msg
        if(ty==3):
            value1=value%10
            value=value/10
            print value
            st=str(value)
            sol=int(value/(10**((len(st)-value1))))
            print sol
            value2=1
            value2=(value2*(len(st)-value1))+int(value%(10**((len(st)-value1))))
            print value
            
            
        
            
    def decrypt_sudoku(self):
        index=self.key%10
        self.key=self.key/10
        rc=self.key%10
        self.key=self.key/10
        print self.key
        tempindex=int(index)
        indexes=[]
        for i in range(len(str(self.key))):
            indexes.append(tempindex)
            tempindex=(tempindex+1)%9
        print indexes
        indexes.reverse()
        print indexes
        self.decryptedValue1=""
        for i in range(len(indexes)):
            index1=indexes[i]
            if(i==(len(indexes)-1)):
                value2=self.identifyValue(self.decryptSudoku[index1])
                if(self.decryptedValue1==""):
                    self.decryptedValue1=str(value2)
                else:
                    self.decryptedValue1=str(value2)+self.decryptedValue1
            else:
                value1=self.key%10
                self.key=self.key/10
                calcValue=self.identifyValue(self.decryptSudoku[index1])
                print calcValue
                value2=calcValue%10
                calcValue=calcValue/10
                calcValue=calcValue*10+value1
                print calcValue
                a=[1,2,3,4,5,6,7,8,9]
                b=calcValue
                n=9
                result=0
                c=[]
                f=[]
                while(n):
                    i=b%n;
                    b=b/n;
                    f.append(i)
                    c.append(a[i])
                    a[i]=a[n-1]
                    n=n-1
                k=self.decryptSudoku[index1]
                self.changeSudoku=[[0]*9 for i in range(9)]
                for i in range(9):
                    for j in range(9):
                        if(i==index1):
                            self.changeSudoku[i][j]=c[j]
                        else:
                            self.changeSudoku[i][j]=c[k.index(self.decryptSudoku[i][j])]
                self.decryptSudoku=self.changeSudoku
                if(self.decryptedValue1==""):
                    self.decryptedValue1=str(value2)
                else:
                    self.decryptedValue1=str(value2)+self.decryptedValue1
        self.decryptedValue=int(self.decryptedValue1)
        self.decryptMessage()
        if(self.decr==0):
            self.button5 = Button(self.master,text="Save", fg="black",command=self.save_sudoku)
            self.button5.pack()
            self.decr=1
            
    def save_sudoku(self):
        sv_sudoku=self.RESULT
        for i in range(9):
            for j in range(9):
                if(sv_sudoku[i][j]=='x'):
                    m=0
                else:
                    sv_sudoku[i][j]=self.encryptSudoku[i][j]
        print sv_sudoku
        complete_save(sv_sudoku)
        fo = open("keyout.txt", "w")
        fo.write(str(self.keyValue));
        fo.close()
                
    def load_sudoku(self):
        self.solved_sudoku=solve_sudoku(self.RESULT)
        self.display(self.solved_sudoku)
        self.change(self.solved_sudoku)
        self.button.destroy()
        self.entry4=IntVar()
        frame1 = Frame(self.master)
        frame1.pack()
        self.l1=Label(frame1,text="Message:",width=7, fg='blue').grid(row=0,column=0)
        self.T = Text(frame1, height=1, width=20)
        self.T.grid(row=0,column=1)
        frame2 = Frame(self.master)
        frame2.pack()
        self.l1=Label(frame2,text="Encrypt on:",width=15, fg='blue').grid(row=0,column=0)
        self.rad_row=Radiobutton(frame2,text="row", variable=self.entry4,value=1)
        self.rad_col=Radiobutton(frame2,text="column", variable=self.entry4,value=2)
        self.rad_row.select()
        self.rad_row.grid(row=0,column=1)
        self.rad_col.grid(row=0,column=2)
        frame3 = Frame(self.master)
        frame3.pack()
        
        self.l1=Label(frame3,text="Select Index:",width=12, fg='blue').grid(row=0,column=0)
        
        choices = [0,1,2,3,4,5,6,7,8]
        self.variable = StringVar(self.master)
        self.variable.set(0)
        self.w = OptionMenu(frame3, self.variable, *choices).grid(row=0,column=1)

        self.button1 = Button(self.master,text="Encrypt", fg="black",command=self.encrypt_sudoku)
        self.button1.pack()
        self.decryptiter=0



if __name__ == "__main__":
    RESULT = OCR(sys.argv[1])
    root = Tk()
    root.geometry("500x500")
    root.title("Conceal Message")
    app = App(root,RESULT)
    root.mainloop()
