import time
import datetime
import os
from abc import ABC, abstractmethod

class HealthcareBotCore(ABC):
    def __init__(self):
        self.symptom_advice = {
            "headache": "\nStay hydrated, rest in a quiet and dark room, and avoid screen time.\nYou can take Paracetamol or Ibuprofen if the pain is mild to moderate.\nIf the headache lasts more than 3 days, gets worse, or is accompanied by vision changes, vomiting, or confusion, seek medical attention immediately.\n",
            "fever": "\nRest well and drink plenty of fluids like water or clear soups.\nYou can take Paracetamol to reduce the fever.\nIf the fever goes above 39°C (102.2°F), lasts more than 2 days, or comes with symptoms like rash, breathing difficulty, or severe headache, see a doctor.\n",
            "cough": "\nStay hydrated and drink warm fluids like tea or soup.\nAvoid smoke and dust.\nA spoon of honey may help soothe your throat (for adults and children over 1 year).\nIf the cough lasts more than 3 weeks, becomes worse, or comes with chest pain, fever, or difficulty breathing, consult a doctor.\n",
            "stomachache": "\nRest and avoid heavy, greasy, or spicy foods.\nEat light meals like rice, toast, or bananas.\nStay hydrated by sipping water or oral rehydration fluids.\nIf the pain is severe, lasts more than a few hours, or comes with vomiting, fever, or blood in stool, seek medical help.\n",
            "cold": "\nRest, drink plenty of warm fluids, and consider using a saline nasal spray to relieve congestion.\nOver-the-counter medications can help with symptoms like runny nose or sore throat.\nIf symptoms last more than 10 days, worsen, or you experience high fever or difficulty breathing, see a doctor.\n",
            "fatigue": "\nMake sure you're getting enough sleep (7-9 hours per night), eating a balanced diet, and staying hydrated.\nGentle exercise like walking can also boost energy levels.\nIf fatigue lasts for more than a few weeks, or comes with symptoms like weight loss, low mood, or shortness of breath, consult a healthcare provider.\n",
            "backpain": "\nTry gentle stretching and avoid heavy lifting or sitting in the same position for too long.\nApplying a warm compress can help relax tight muscles.\nOver-the-counter pain relief like Ibuprofen may help.\nIf the pain is severe, lasts more than a week, or spreads to your legs, seek medical attention.\n"
        }
        self.medications_info = {
            "Paracetamol": "Used to relieve pain and reduce fever.",
            "Ibuprofen": "Anti-inflammatory medication used for pain and inflammation.",
            "Amoxicillin": "An antibiotic used to treat bacterial infections.",
            "Cetirizine": "An antihistamine used for allergy relief.",
            "Metformin": "Used to control high blood sugar in type 2 diabetes."
        }

    @abstractmethod
    def display_menu(self):
        pass

    def validate_date_format(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def parse_date(self, date_text):
        try:
            return datetime.datetime.strptime(date_text, '%Y-%m-%d').date()
        except ValueError:
            return None

    def validate_time_format(self, time_text):
        if len(time_text) != 5 or time_text[2] != ":":
            return False
        try:
            hour, minute = time_text.split(":")
            if not (hour.isdigit() and minute.isdigit()):
                return False
            h, m = int(hour), int(minute)
            return 0 <= h <= 23 and 0 <= m <= 59
        except:
            return False

class UserManagement(HealthcareBotCore):
    def __init__(self):
        super().__init__()
        self.user_name = ""
        self.user_age = None
        self.user_gender = ""
        self.appointments = []
        self.medication_schedule = {}

    def welcome(self):
        print("Hello! I am your Healthcare Assistant Bot ")
        time.sleep(1)
        print("I can help you with symptom checking, appointment scheduling, medication reminders, and health advice.")
        time.sleep(1)
        self.get_user_info()
        self.save_user_to_file()

    def get_user_info(self):
        print("\nLet's start with some basic info about you.")
        self.user_name = input("What is your name? ").strip().title()
        while not self.user_name:
            print("Please enter a valid name.")
            self.user_name = input("What is your name? ").strip().title()
        while True:
            age_input = input("How old are you? (between 6 and 120) (in years) ").strip()
            if age_input.isdigit() and 6 <= int(age_input) < 120:
                self.user_age = int(age_input)
                break
            else:
                print("Invalid Age Provided. Please enter a valid age.")
        while True:
            gender_input = input("What is your gender? (Male/Female/Other) ").strip().lower()
            if gender_input in ['male', 'female', 'other']:
                self.user_gender = gender_input.title()
                break
            else:
                print("Please enter Male, Female, or Other.")
        print(f"\nThank you, {self.user_name}. How can I assist you today?")
        time.sleep(1)

    def save_user_to_file(self):
        # Sanitize filename to prevent directory traversal errors
        safe_name = "".join([c for c in self.user_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"users/{safe_name}.txt"
        os.makedirs("users", exist_ok=True)
        try:
            with open(filename, "w") as f:
                f.write(f"Name: {self.user_name}\n")
                f.write(f"Age: {self.user_age}\n")
                f.write(f"Gender: {self.user_gender}\n")
                f.write("Appointments:\n")
                if self.appointments:
                    for appt in sorted(self.appointments, key=lambda x: (x['date'], x['time'])):
                        f.write(f" Doctor: {appt['dr']}  Date: {appt['date']}, Time: {appt['time']}, Reason: {appt['reason']}\n")
                else:
                    f.write("  No appointments scheduled.\n")
                f.write("Medications:\n")
                if self.medication_schedule:
                    for med, times in self.medication_schedule.items():
                        f.write(f"  {med}: {', '.join(times)}\n")
                else:
                    f.write("  No medications scheduled.\n")
        except Exception as e:
            print(f"Error saving user data: {e}")

    def load_user_from_file(self, username):
        safe_name = "".join([c for c in username if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"users/{safe_name}.txt"
        if not os.path.exists(filename):
            print(f"No data found for user '{username}'.")
            return
        try:
            with open(filename, "r") as file:
                print(file.read())
        except Exception as e:
            print(f"Error reading user data: {e}")

    def list_all_users(self):
        os.makedirs("users", exist_ok=True)
        users = []
        try:
            for file in os.listdir("users"):
                if file.endswith(".txt"):
                    users.append(file[:-4])
            return users
        except Exception as e:
            print(f"Error listing user files: {e}")
            return []

    def delete_user_file(self, username):
        safe_name = "".join([c for c in username if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"users/{safe_name}.txt"
        if not os.path.exists(filename):
            print(f"No data found for user '{username}'.")
            return
        try:
            os.remove(filename)
            print(f"User data for '{username}' deleted successfully.")
        except Exception as e:
            print(f"Error deleting user data: {e}")

    def display_menu(self):
        print("\nUser Management Menu:")
        print("1. View User Information")
        print("2. Update User Information")
        print("3. Back to Main Menu")

class HealthcareBot(UserManagement):
    def __init__(self):
        super().__init__()

    def display_menu(self):
        options = {
            '1': 'User Management',
            '2': 'Symptoms You Experience',
            '3': 'Get Health Advice',
            '4': 'Schedule Appointment To Respective Doctors',
            '5': 'View Appointments',
            '6': 'Manage Medication Reminders',
            '7': 'View Medication Schedule',
            '8': 'Manage User History',
            '9': 'Exit'
        }
        print("\nMain Menu:")
        for i, j in options.items():
            print(f"  {i}. {j}")

    def main_menu(self):
        while True:
            self.display_menu()
            choice = input("Select an option (1-9): ").strip()
            if choice == '1':
                self.user_management_menu()
            elif choice == '2':
                self.check_symptoms()
            elif choice == '3':
                self.get_health_advice()
            elif choice == '4':
                self.schedule_appointment()
            elif choice == '5':
                self.view_appointments()
            elif choice == '6':
                self.medication_reminder_menu()
            elif choice == '7':
                self.view_medication_schedule()
            elif choice == '8':
                self.user_history_menu()
            elif choice == '9':
                print(f"\nThank you for using the Healthcare Assistant Bot, {self.user_name}. Take care! ")
                break
            else:
                print("Invalid choice.\nPlease select a number between 1 and 9.")

    def user_management_menu(self):
        while True:
            super().display_menu()
            choice = input("Select an option (1-3): ").strip()
            if choice == '1':
                self.view_user_info()
            elif choice == '2':
                self.update_user_info()
                self.save_user_to_file()
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please select 1-3.")

    def view_user_info(self):
        print("\nUser Information:")
        print(f"Name: {self.user_name}")
        print(f"Age: {self.user_age}")
        print(f"Gender: {self.user_gender}")

    def update_user_info(self):
        print("\nUpdate User Information (leave blank to keep current value):")
        new_name = input(f"Name [{self.user_name}]: ").strip().title()
        if new_name:
            self.user_name = new_name

        while True:
            new_age = input(f"Age [{self.user_age}]: ").strip()
            if not new_age:
                break
            if new_age.isdigit() and 0 < int(new_age) < 120:
                self.user_age = int(new_age)
                break
            else:
                print("Please enter a valid age.")

        while True:
            new_gender = input(f"Gender [{self.user_gender}]: ").strip().lower()
            if not new_gender:
                break
            if new_gender in ['male', 'female', 'other']:
                self.user_gender = new_gender.title()
                break
            else:
                print("Please enter Male, Female, or Other.")

        print("User information updated successfully.")

    def check_symptoms(self):
        print("\nSymptom Checker")
        print("You can type 'list' to see common symptoms or 'back' to return to the main menu.")
        while True:
            symptom = input("Enter your symptom: ").strip().lower()
            if symptom == 'back':
                break
            elif symptom == 'list':
                print("Common Symptoms:")
                for s in self.symptom_advice.keys():
                    print(f" - {s.title()}")
            elif symptom in self.symptom_advice:
                print(f"Advice for {symptom.title()}:")
                print(f"  {self.symptom_advice[symptom]}")
            else:
                print("Sorry, I don't have advice for that symptom. Please try another or type 'list' to see common symptoms.")

    def get_health_advice(self):
        print("\nHealth Advice")
        print("You can type 'topics' to see common advice topics or 'back' to return.")
        advice_topics = {
            "diet": "Eat a variety of whole foods including fruits, vegetables, whole grains, and lean proteins.\nLimit sugar, salt, and processed foods while staying hydrated.\nPractice portion control and mindful eating for long-term balance.",
            "exercise": "Aim for at least 30 minutes of moderate exercise most days of the week.\nInclude a mix of cardio, strength training, and flexibility exercises.\nStay consistent, listen to your body, and make movement a daily habit.",
            "hydration": "Drink 6-8 glasses of water daily, more if you're active or in a hot climate.\nChoose water over sugary or caffeinated drinks whenever possible.\nPay attention to thirst and urine color - being clear or light yellow means you're well-hydrated.",
            "sleep": "Aim for 7-9 hours of quality sleep each night to support overall health.\nMaintain a consistent sleep schedule, even on weekends.\nLimit screen time before bed and create a calm, dark sleeping environment.",
            "stress": "Practice relaxation techniques like deep breathing, meditation, or yoga daily.\nStay physically active and connect regularly with supportive people.\nPrioritize self-care, set boundaries, and take breaks to recharge.",
            "mental health": "Talk openly about your feelings and seek support when needed - you're not alone.\nMaintain a healthy lifestyle with regular sleep, exercise, and balanced nutrition.\nEngage in activities you enjoy and take time to rest and reflect."
        }
        while True:
            topic = input("Enter a topic for advice: ").strip().lower()
            if topic == 'back':
                break
            elif topic == 'topics':
                print("Common advice topics:")
                for t in advice_topics:
                    print(f" - {t.title()}")
            elif topic in advice_topics:
                print(f"Advice on {topic.title()}:")
                print(f"  {advice_topics[topic]}")
            else:
                print("Topic not recognized. Type 'topics' to see available ones.")

    def schedule_appointment(self):
        print("\nAppointment Scheduling")
        drs_dict = {
            "Dr. S. Ramakrishnan": "Cardiology (Founder of Sri Ramakrishna Hospital, Coimbatore)",
            "Dr. Prithika Chary": "Neurology (Senior Consultant Neurologist & Neurosurgeon, Kauvery Hospital, Chennai)",
            "Dr. K. M. Cherian": "Cardiothoracic Surgery (Founder of Frontier Lifeline Hospital, Chennai)",
            "Dr. Mohan V": "Diabetology (Chairman of Dr. Mohan Diabetes Specialities Centre, Chennai)",
            "Dr. J. S. Rajkumar": "Laparoscopic Surgery (Founder of Lifeline Hospitals, Chennai)"
        }
        dr_list = list(drs_dict.keys())
        
        print("You can type 'back' at any time to return.")
        print("Available Renowned doctors of Tamil Nadu:")
        for idx, name in enumerate(dr_list, 1):
            print(f"{idx}. {name} - {drs_dict[name]}")
        print()

        while True:
            choice = input("Select doctor by number: ").strip()
            if choice.lower() == 'back': return
            if choice.isdigit() and 1 <= int(choice) <= len(dr_list):
                dr_name = dr_list[int(choice)-1]
                break
            print("Invalid selection. Please choose a number from the list.")

        while True:
            date_str = input("Enter appointment date (YYYY-MM-DD): ").strip()
            if date_str.lower() == 'back': return
            if not self.validate_date_format(date_str):
                print("Invalid date format. Please enter date as YYYY-MM-DD.")
                continue
            date_obj = self.parse_date(date_str)
            if date_obj is None or date_obj < datetime.date.today():
                print("Date must be today or in the future.")
                continue
            
            time_str = input("Enter appointment time (HH:MM, 24h format): ").strip()
            if time_str.lower() == 'back': return
            if not self.validate_time_format(time_str):
                print("Invalid time format. Please enter time as HH:MM.")
                continue
            
            reason = input("Enter reason for appointment: ").strip()
            if not reason:
                print("Reason cannot be empty.")
                continue

            conflict = False
            for i in self.appointments:
                if (i["dr"] == dr_name) and (i["date"] == date_str) and (i["time"] == time_str):
                    print("Sorry! This slot is already booked for this doctor.")
                    conflict = True
                    break
            
            if not conflict:
                appt = {"dr": dr_name, "date": date_str, "time": time_str, "reason": reason}
                self.appointments.append(appt)
                self.save_user_to_file()
                print(f"Appointment with {dr_name} scheduled on {date_str} at {time_str} for '{reason}'.")
                break

    def view_appointments(self):
        print("\nYour Scheduled Appointments:")
        if not self.appointments:
            print("You have no appointments scheduled.")
            return
        
        sorted_appts = sorted(self.appointments, key=lambda x: (x['date'], x['time']))
        for i, appt in enumerate(sorted_appts, 1):
            print(f"  {i}. Doctor: {appt['dr']} | Date: {appt['date']}, Time: {appt['time']}, Reason: {appt['reason']}")

        print("\nOptions:")
        print("1. Back to main menu")
        print("2. Cancel an appointment")
        choice = input("Select an option (1-2): ").strip()

        if choice == '2':
            self.cancel_appointment()
        elif choice != '1':
            print("Returning to main menu.")

    def cancel_appointment(self):
        if not self.appointments:
            print("No appointments to cancel.")
            return

        print("\nCancel Appointment")
        sorted_appts = sorted(self.appointments, key=lambda x: (x['date'], x['time']))
        for i, appt in enumerate(sorted_appts, 1):
            print(f"  {i}. Doctor: {appt['dr']} | Date: {appt['date']}, Time: {appt['time']}")

        while True:
            choice = input("\nEnter the number of the appointment to cancel (or 'back'): ").strip()
            if choice.lower() == 'back':
                return

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(sorted_appts):
                    appt_to_remove = sorted_appts[idx]
                    confirm = input(f"Cancel appointment with {appt_to_remove['dr']} on {appt_to_remove['date']}? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        self.appointments.remove(appt_to_remove)
                        self.save_user_to_file()
                        print("Appointment cancelled.")
                        return
                    else:
                        print("Cancellation aborted.")
                        return
                else:
                    print("Invalid number.")
            else:
                print("Please enter a valid number.")

    def medication_reminder_menu(self):
        options = {
            '1': 'Add Medication',
            '2': 'Remove Medication',
            '3': 'List Medications',
            '4': 'Back to Main Menu'
        }
        print("\nCommon Medication Examples:")
        for med in self.medications_info:
            print(f"- {med}")
            
        while True:
            print("\nMedication Reminder Menu:")
            for key, val in options.items():
                print(f"  {key}. {val}")
            choice = input("Select an option (1-4): ").strip()
            if choice == '1':
                self.add_medication()
            elif choice == '2':
                self.remove_medication()
            elif choice == '3':
                self.list_medications()
            elif choice == '4':
                break
            else:
                print("Invalid option.")

    def add_medication(self):
        print("\nAdd Medication")
        med_name = input("Medication name: ").strip().title()
        if not med_name:
            print("Medication name cannot be empty.")
            return
        
        description = self.medications_info.get(med_name, "No specific info available.")
        print(f"Info: {description}")
        
        times_str = input("Enter reminder times separated by comma (HH:MM format, 24h): ").strip()
        times = [t.strip() for t in times_str.split(",")]
        valid_times = []
        for t in times:
            if self.validate_time_format(t):
                valid_times.append(t)
            else:
                print(f"Warning: '{t}' skipped (invalid format).")
        
        if not valid_times:
            print("No valid times entered.")
            return
            
        self.medication_schedule[med_name] = valid_times
        self.save_user_to_file()
        print(f"Added '{med_name}' at: {', '.join(valid_times)}")

    def remove_medication(self):
        if not self.medication_schedule:
            print("No medications to remove.")
            return
        meds = list(self.medication_schedule.keys())
        for i, med in enumerate(meds, 1):
            print(f"  {i}. {med}")
        choice = input("Select number to remove: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(meds):
            removed = meds[int(choice)-1]
            del self.medication_schedule[removed]
            self.save_user_to_file()
            print(f"Removed {removed}.")
        else:
            print("Invalid selection.")

    def list_medications(self):
        print("\nYour Medication Schedule:")
        if not self.medication_schedule:
            print("No medications scheduled.")
            return
        for med, times in self.medication_schedule.items():
            print(f"  {med}: at {', '.join(times)}")

    def view_medication_schedule(self):
        self.list_medications()

    def user_history_menu(self):
        options = {
            '1': 'List All Users',
            '2': 'View User Details',
            '3': 'Delete User History',
            '4': 'Back to Main Menu'
        }
        while True:
            print("\nUser History Menu:")
            for k, v in options.items():
                print(f"  {k}. {v}")
            choice = input("Select an option (1-4): ").strip()
            if choice == '1':
                users = self.list_all_users()
                if users:
                    print("Users found:")
                    for u in users: print(f" - {u}")
                else:
                    print("No user data found.")
            elif choice == '2':
                username = input("Enter the username: ").strip()
                self.load_user_from_file(username)
            elif choice == '3':
                username = input("Enter the username to delete: ").strip()
                confirm = input(f"Are you sure? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    self.delete_user_file(username)
            elif choice == '4':
                break

bot = HealthcareBot()
bot.welcome()
bot.main_menu()