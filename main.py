import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import *
from PIL import Image, ImageTk
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
from logic import HandClassifierHandler
import time


class MyApp:
    def __init__(self, root, hch, model):
        self.root = root
        self.root.title("ALFABET POLSKIEGO JĘZYKA MIGOWEGO")
        self.root.configure(bg="#f0f0f0")

        self.alphabet_video = "res/ABC.mp4"
        # TODO do poprawy
        self.task_list = [7, 13, 6, 9, 14, 16, 8, 18, 21, 12]
        self.score = 0

        self.frame = ttk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        self.create_widgets(hch, model)

        self.show_welcome_activity()

    def create_widgets(self, hch, model):
        style = ttk.Style()
        style.configure("Green.TButton", background="#4CAF50", foreground="white", font=("Arial", 16))

        # Welcome Activity #############################################################################################
        mess = "PODAJ SWOJE IMIĘ:"
        self.label_welcome = ttk.Label(self.frame, font=("Arial", 16), text=mess)
        self.label_welcome.pack(pady=10)

        self.entry_name = ttk.Entry(self.root, font=("Arial", 14), width=30)
        self.entry_name.pack(pady=20)


        self.btn_activity1 = ttk.Button(self.frame, text="START", command=self.show_video_activity, style="Green.TButton")
        self.btn_activity1.pack(pady=40)



        # Display alphabet video ######################################################################################
        self.label_video = ttk.Label(self.frame,
                                     text="Zapoznaj się z materiałem poniżej, następnie spróbuj odwzorować podane znaki")
        self.label_video.pack(pady=20)

        self.video_label = ttk.Label(self.frame)
        self.video_label.pack(pady=20)

        self.btn_activity2 = ttk.Button(self.frame, text="ROZPOCZNIJ", command=self.show_camera_activity)
        self.btn_activity2.pack()



        # Classify hands activity ######################################################################################
        self.label_image = ttk.Label(self.frame, text="Pokaż znak do kamery")
        self.label_image.pack(pady=20)

        self.image_label = ttk.Label(self.frame)
        self.image_label.pack(pady=20)

        self.btn_activity3 = ttk.Button(self.frame, text="SPRAWDŹ", command=self.check_name)
        self.btn_activity3.pack()


    def show_welcome_activity(self):
        self.label_welcome.pack()
        self.entry_name.pack()
        self.btn_activity1.pack()
        self.label_video.pack_forget()
        self.video_label.pack_forget()
        self.btn_activity2.pack_forget()
        self.label_image.pack_forget()
        self.image_label.pack_forget()
        self.btn_activity3.pack_forget()

    def show_video_activity(self):

        self.name = self.entry_name.get()

        if len(self.name) ==0:
            self.name = "imię"
        self.name_code = []

        for l in self.name:
            self.name_code.append(self.get_numbers(l))
        print(self.name)
        print(self.name_code)
        # if not self.name or not self.name.isascii():
        #     tk.messagebox.showerror("Error", "Please enter a valid name.")
        #     return

        self.label_welcome.pack_forget()
        self.btn_activity1.pack_forget()
        self.entry_name.pack_forget()
        self.label_video.pack()
        self.video_label.pack()
        self.btn_activity2.pack()
        self.label_image.pack_forget()
        self.image_label.pack_forget()
        self.btn_activity3.pack_forget()

        self.show_wideo()

    def show_wideo(self):
        self.cap = cv2.VideoCapture(self.alphabet_video)

        def update_video():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (1000, 900))
                imgPIL = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(imgPIL)
                self.video_label.configure(image=imgtk)
                self.video_label.image = imgtk
                self.video_label.after(10, update_video)
            else:
                self.cap.release()
                #self.video_label.pack_forget()

        update_video()

    def show_camera_activity(self):

        self.label_welcome.pack_forget()
        self.btn_activity1.pack_forget()
        self.entry_name.pack_forget()
        self.label_video.pack_forget()
        self.video_label.pack_forget()
        self.btn_activity2.pack_forget()
        self.label_image.pack()
        self.image_label.pack()
        self.btn_activity3.pack_forget()

        self.capture_camera()



    def capture_camera(self):
        self.cnt = 0
        past = []
        self.imie = []
        letter = self.get_letters(self.task_list[self.cnt])
        self.label_image.config(text=letter)
        self.cap = cv2.VideoCapture(0)
        start_time = time.time()

        def select_img():

            with mp_hands.Hands(
                    model_complexity=0,
                    max_num_hands=1,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.5) as hands:
                _, img = self.cap.read()
                img = cv2.resize(img, (1000, 900))
                img.flags.writeable = False
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = hands.process(img)
                # Draw the hand annotations on the image:
                img.flags.writeable = True
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    message = results.multi_handedness
                    # obtain result from classificator:
                    result = hch.get_result(model=model, handlandmarks=results.multi_hand_landmarks[0],
                                            is_R=hch.is_right(message))

                    past.append(result)

                    if self.cnt < len(self.task_list)-1:
                        if result == self.task_list[self.cnt]:
                            if len(past) > 5:
                                last_elements = past[-3:]
                                # sprawdzenie czy ostatnie są też takie czy to był przypadek:
                                are_equal = all(element == self.task_list[self.cnt] for element in last_elements)
                                if are_equal:
                                    self.cnt += 1
                                    letter = self.get_letters(self.task_list[self.cnt])
                                    self.label_image.config(text=letter)
                                    self.score +=1
                    else:
                        #imie
                        polecenie = "Przeliteruj: " + self.name
                        self.label_image.config(text=polecenie)
                        self.imie.append(result)
                        self.btn_activity3.pack()




                    result_name = hch.result_parser(result=result)

                    # check which hand:
                    if hch.is_right(message):
                        print('Right')
                    else:
                        print('Left')
                    # draw handlandmarks on image:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            img,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())

                # Flip the image horizontally for a selfie-view display: cv2.flip(image, 1)
                # or leave for more video like effect
                imgPIL = Image.fromarray(cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(imgPIL)

                if time.time() - start_time > 600:
                    self.cnt += 1
                    if self.cnt < len(self.task_list)-1:
                        letter = self.get_letters(self.task_list[self.cnt])
                        self.label_image.config(text=letter)



                self.image_label.configure(image=imgtk)
                self.image_label.image = imgtk
                self.image_label.after(10, select_img)

        select_img()



    def get_letters(self, num):
        class_nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                      11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                      21, 22, 23, 24, 25, 26, 27, 28]
        class_names = ["0", "1", "2", "3", "4", "5", "A", "B",
                       "C", "D", "E", "F", "H", "I", "L",
                       "M", "N", "P", "R", "S", "U", "W", "Y",
                       "Aw", "Bk", "Cm", "Ik", "Om", "Um"]
        return class_names[num]

    def get_numbers(self, letter):
        letter = letter.lower()
        letter_num = -1
        class_nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                      11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                      21, 22, 23, 24, 25, 26, 27, 28]
        class_names = ["O", "1", "2", "3", "4", "5", "A", "B",
                       "C", "D", "E", "F", "H", "I", "L",
                       "M", "N", "P", "R", "S", "U", "W", "Y",
                       "Aw", "Bk", "Cm", "Ik", "Om", "Um"]

        letters = ["a", "ą", "b", "c", "ć", "d", "e", "ę","f", "g", "h", "i", "j",
                       "k", "l", "ł", "m", "n", "ń", "o", "ó", "p", "r", "s", "ś",
                       "t", "u", "w", "y", "z", "ź", "ż"]

        for index, element in enumerate(letters):
            if element == letter:
                if element in ["ą","ć","ę", "ł", "ń","ó","ś","ź",]:
                    letter = letters[index - 1]
                if element in ["ż"]:
                    letter = letters[index - 2]

        for index, element in enumerate(class_names):
            if element.lower() == letter:
                letter_num = index
            if letter == "k":
                letter_num = 3
            if letter =="g":
                letter_num =  10
            if letter =="j":
                letter_num =  13
            if letter =="t":
                letter_num =  11
            if letter =="z":
                letter_num = 9

        return letter_num







    def check_answer(self,codes_list, answer_list):
        # znajdx początek:
        start_n = -1
        for idx, elem in enumerate(codes_list):
            if elem[0] == answer_list[0]:
                start_n = idx
                print(start_n)
                break


        codes_list_cut = codes_list[start_n:-1]
        # clean_codes=[]
        # # usuniecie pojedynczych wartości
        # if len(codes_list_cut) > 2:
        #     for i in range(1, len(codes_list_cut)-1):
        #         if codes_list_cut[i] != codes_list_cut[i - 1] and codes_list_cut[i] != codes_list_cut[i + 1]:
        #             clean_codes.append(codes_list_cut[i])
        # else:
        #     clean_codes=codes_list_cut

        print(codes_list_cut)
        # sprawdzenie kolejności:
        idx1=0
        idx2=0

        while idx1 < len(codes_list_cut) and idx2 < len(answer_list):
            if codes_list_cut[idx1][0] == answer_list[idx2]:
                idx2 += 1
            idx1 += 1
        if (idx2 == len(answer_list)):
            return True
        else:
            return False











    def code_name(self):
        pass

    def check_name(self):
        signs_list = self.name
        if len(self.name) ==0:
            # TODO messagebox
            pass
        else:
            print(self.name)
            print(self.imie)
            print(self.check_answer(self.imie, self.name_code))






if __name__ == "__main__":
    hch = HandClassifierHandler.HandClassifierHandler()
    model = hch.load_model()

    root = tk.Tk()
    app = MyApp(root, hch, model)
    root.geometry("1200x800")
    root.mainloop()
