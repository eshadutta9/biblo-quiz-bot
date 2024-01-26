import tkinter as tk
from tkinter import messagebox
from read_json_config import read_json

class QuizApp:
    def __init__(self, master, question_dict, furhat_conn):
        self.master = master
        self.question_dict = question_dict
        self.current_question_index = 0
        self.selected_option = tk.StringVar()
        self.is_correct = False
        self.option_to_return = ""
        self.furhat = furhat_conn
        self.create_widgets()

    def create_widgets(self):
        # Question Label
        self.question_label = tk.Label(self.master, text=self.question_dict['question'], font=('Arial', 14))
        self.question_label.pack(pady=10)

        # Options Radio Buttons
        for option in self.question_dict['options']:
            tk.Radiobutton(self.master, text=option, variable=self.selected_option, value=option).pack(anchor='w')

        # Hint Button
        hint_button = tk.Button(self.master, text='Hint', command=self.give_hint)
        hint_button.pack(pady=10)
        
        # Submit Button
        submit_button = tk.Button(self.master, text='Submit', command=self.check_answer)
        submit_button.pack(pady=10)

        

    def give_hint(self):
        self.furhat.furhat_speak(self.question_dict["hint"])

    def check_answer(self):
        self.option_to_return = self.selected_option.get()
        # if possible, show the answer on the same screen only, and then an OK button to move on -> now we cannot see the correct answer vs other options
        self.master.destroy()
        # is_correct = False
        # selected_answer = self.selected_option.get()
        # correct_answer = self.question_dict['correct']
        # print("selected_answer : ", selected_answer)
        # print("correct_answer : ", correct_answer)
        # if selected_answer[0] == correct_answer:
        #     self.is_correct = True
        #     messagebox.showinfo('Result', 'Correct! Well done.')
        # else:
        #     messagebox.showinfo('Result', f'Incorrect. The correct answer is {correct_answer}.')
        # self.master.destroy()
        # Move to the next question
        # self.current_question_index += 1

        # if self.current_question_index < len(questions):
        #     self.update_question()
        # else:
        #     messagebox.showinfo('Quiz Complete', 'You have completed the quiz!')

    # def update_question(self):
    #     self.selected_option.set('')  # Clear the selected option
    #     self.question_dict = questions[self.current_question_index]
    #     self.question_label.config(text=self.question_dict['question'])

def session_start():
    root = tk.Tk()
    root.title('Session Start')
    messagebox.showinfo("Let's start!")
    root.destroy()

def render_ui(questions, furhat_conn):
    root = tk.Tk()
    root.title('Quiz App')
    # root.withdraw()
    # questions = [questions]

    # Create an instance of the QuizApp class
    quiz_app = QuizApp(root, questions, furhat_conn)

    # Run the Tkinter main loop
    root.mainloop()
    return quiz_app.option_to_return[0]

def show_evaluation(is_correct, question):
    root = tk.Tk()
    root.title('Result')
    options = str(question["options"]).replace("'","")
    options = options.replace("[","")
    options = options.replace("]","")
    if(is_correct):
        messagebox.showinfo('Result', f'Correct! Well done.')
    else:
        messagebox.showinfo('Result', f'Question: {question["question"]}\n Options: {options}\n Incorrect. The correct answer is {question["correct"]}. You chose {question["choice"]}')
    root.destroy()
    
