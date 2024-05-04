from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json

TASKS_JSON_FILE = "tasks.json"

class Task(ABC):
    personal_task_count = 0
    work_task_count = 0
    
    def __init__(self, name, deadline, priority, color, **kwargs):
        if isinstance(self, PersonalTask):
            Task.personal_task_count += 1
            self.task_number = Task.personal_task_count
        elif isinstance(self, WorkTask):
            Task.work_task_count += 1
            self.task_number = Task.work_task_count
        
        self.name = name
        self.deadline = deadline
        self.priority = priority
        self.color = color
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def remaining_days(self):
        pass

    def add_note(self, note):
        self.note = note

class PersonalTask(Task):
    def __init__(self, name, deadline, priority, color, task_status="pending", **kwargs):
        task_number = kwargs.pop("task_number", None)
        super().__init__(name, deadline, priority, color, task_status=task_status, **kwargs)
        self.task_number = task_number

    def remaining_days(self):
        today = datetime.now().date()
        deadline_date = datetime.strptime(self.deadline, "%d/%m/%Y").date()
        remaining = (deadline_date - today).days
        if remaining == 0:
            return "Today", remaining
        elif remaining == 1:
            return "Tomorrow", remaining
        elif remaining <= 7:
            return deadline_date.strftime('%A'), remaining
        elif remaining <= 14:
            return "Next Week", remaining
        elif remaining <= 30:
            return "This Month", remaining
        elif remaining <= 60:
            return "Next Month", remaining
        else:
            return "There is still more time.", remaining

class WorkTask(Task):
    def __init__(self, name, deadline, priority, color, task_status="pending", **kwargs):
        task_number = kwargs.pop("task_number", None)
        super().__init__(name, deadline, priority, color, task_status=task_status, **kwargs)
        self.task_number = task_number

    def remaining_days(self):
        today = datetime.now().date()
        deadline_date = datetime.strptime(self.deadline, "%d/%m/%Y").date()
        remaining = (deadline_date - today).days
        return remaining, deadline_date.strftime('%d/%m/%Y')
    
class TaskEditing:
    def __init__(self, task_management):
        self.task_management = task_management

    def edit_task(self):
        task_identifier = input("Enter the name or number of the task you want to edit: ")
        similar_tasks = self.find_similar_tasks(task_identifier)

        if not similar_tasks:
            print("No matching tasks found. Please enter a valid task name or number.")
            return

        print(f"{len(similar_tasks)} matching tasks found.")
        self.print_similar_tasks(similar_tasks)

        task_index = input("Enter the index of the task you want to edit: ")
        try:
            task_index = int(task_index)
        except ValueError:
            print("Invalid input. Please enter a valid index.")
            return

        if not (0 <= task_index < len(similar_tasks)):
            print("Invalid index. Please enter a valid index.")
            return

        task_to_edit = similar_tasks[task_index]

        new_name = input(f"Enter new name for the task '{task_to_edit.name}': ").strip()
        new_deadline = input(f"Enter new deadline for the task '{task_to_edit.deadline}' (format: dd/mm/yyyy): ").strip()
        new_priority = input(f"Enter new priority for the task '{task_to_edit.priority}': ").strip()
        new_color = input(f"Enter new color for the task '{task_to_edit.color}': ").strip()

        if new_name:
            task_to_edit.name = new_name
        if new_deadline:
            task_to_edit.deadline = new_deadline
        if new_priority:
            task_to_edit.priority = new_priority
        if new_color:
            task_to_edit.color = new_color

        print("Task updated successfully.")

    def find_similar_tasks(self, task_identifier):
        similar_tasks = []
        for task in self.task_management.tasks:
            if task.name.lower().find(task_identifier.lower()) != -1 or str(task.task_number) == task_identifier:
                similar_tasks.append(task)
        return similar_tasks

    def print_similar_tasks(self, similar_tasks):
        print("Matching tasks found:")
        for i, task in enumerate(similar_tasks):
            print(f"Index: {i}, Name: {task.name}, Deadline: {task.deadline}, Priority: {task.priority}, Color: {task.color}")

    def delete_task(self):
        task_identifier = input("Enter the name or number of the task you want to delete: ")
        similar_tasks = self.find_similar_tasks(task_identifier)

        if not similar_tasks:
            print("No matching tasks found. Please enter a valid task name or number.")
            return

        print(f"{len(similar_tasks)} matching tasks found.")
        self.print_similar_tasks(similar_tasks)

        task_index = input("Enter the index of the task you want to delete: ")
        try:
            task_index = int(task_index)
        except ValueError:
            print("Invalid input. Please enter a valid index.")
            return

        if not (0 <= task_index < len(similar_tasks)):
            print("Invalid index. Please enter a valid index.")
            return

        task_to_delete = similar_tasks[task_index]
        self.task_management.tasks.remove(task_to_delete)
        print("Task deleted successfully.")

class TaskManagement:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def mark_task_completed(self, task_name):
        for task in self.tasks:
            if task.name == task_name:
                task.task_status = "completed"
                print(f"Task '{task_name}' marked as completed.")
                break
        else:
            print(f"Task '{task_name}' not found.")

    def get_task_status(self, task_name):
        for task in self.tasks:
            if task.name == task_name:
                return task.task_status
        print(f"Task '{task_name}' not found.")
        return None

    def save_to_json(self):
        with open(TASKS_JSON_FILE, 'w') as file:
            json.dump([task.__dict__ for task in self.tasks], file, indent=4)

    def load_from_json(self):
        try:
            with open(TASKS_JSON_FILE, 'r') as file:
                data = json.load(file)
                personal_task_index = 1
                work_task_index = 1
                for task_data in data:
                    task_number = task_data.pop("task_number", None)
                    if task_data["type"] == "PersonalTask":
                        if task_number is None:
                            task_number = personal_task_index
                            personal_task_index += 1
                        task = PersonalTask(task_number=task_number, **task_data)
                    elif task_data["type"] == "WorkTask":
                        if task_number is None:
                            task_number = work_task_index
                            work_task_index += 1
                        task = WorkTask(task_number=task_number, **task_data)
                    self.add_task(task)
        except FileNotFoundError:
            print(f"File '{TASKS_JSON_FILE}' not found.")

    def print_pending_tasks(self):
        personal_tasks = [task for task in self.tasks if isinstance(task, PersonalTask) and task.task_status == "pending"]
        work_tasks = [task for task in self.tasks if isinstance(task, WorkTask) and task.task_status == "pending"]

        for task in personal_tasks:
            remaining_days = task.remaining_days()
            print(f"PersonalTask: {task.task_number}, {task.name}, {remaining_days[0]}, {task.color}, Priority: {task.priority}, Remaining Days: {remaining_days[1]}, Task status: {task.task_status}")

        for task in work_tasks:
            remaining_days = task.remaining_days()
            print(f"WorkTask: {task.task_number}, {task.name}, {remaining_days[1]}, {task.color}, Priority: {task.priority}, Remaining Days: {remaining_days[0]}, Task status: {task.task_status}")

    def print_tasks(self):
        personal_tasks = []
        work_tasks = []  
        for task in self.tasks:
            remaining_days = task.remaining_days()
            if isinstance(task, PersonalTask):
                personal_tasks.append((task, remaining_days))
            elif isinstance(task, WorkTask):
                work_tasks.append((task, remaining_days))
        personal_tasks.sort(key=lambda x: x[0].task_number)
        work_tasks.sort(key=lambda x: x[0].task_number)
        
        for task, remaining_days in personal_tasks:
            note = getattr(task, 'note', None)
            if note:
                print(f"PersonalTask: {task.task_number}, {task.name}, {remaining_days[0]}, {task.color}, Priority: {task.priority}, Remaining Days: {remaining_days[1]}, Task status: {task.task_status}, Note: {note}")
            else:
                print(f"PersonalTask: {task.task_number}, {task.name}, {remaining_days[0]}, {task.color}, Priority: {task.priority}, Remaining Days: {remaining_days[1]}, Task status: {task.task_status}")

        for task, remaining_days in work_tasks:
            note = getattr(task, 'note', None)
            if note:
                print(f"WorkTask: {task.task_number}, {task.name}, {remaining_days[1]}, {task.color}, Priority: {task.priority}, Remaining Days: {remaining_days[0]}, Task status: {task.task_status}, Note: {note}")
            else:
                print(f"WorkTask: {task.task_number}, {task.name}, {remaining_days[1]}, {task.color}, Priority: {task.priority}, Remaining Days: {remaining_days[0]}, Task status: {task.task_status}")


class TaskScheduling:
    def __init__(self, task_management):
        self.task_management = task_management

    def get_user_choice(self, options):
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")
        while True:
            choice = input("Enter your choice: ")
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return int(choice)
            else:
                print("Invalid choice. Please enter a valid number.")

    def create_personal_task_from_input(self):
        name = input("Enter task name: ")
        deadline = input("Enter task deadline (format: dd/mm/yyyy): ")
        priorities = ["low", "medium", "high", "urgent"]
        priority = priorities[self.get_user_choice(priorities) - 1]
        colors = ["red", "blue", "green", "yellow"]
        color = colors[self.get_user_choice(colors) - 1]
        task_number = len([task for task in self.task_management.tasks if isinstance(task, PersonalTask)]) + 1
        task_data = {
            "name": name,
            "deadline": deadline,
            "priority": priority,
            "color": color,
            "task_status": "pending",
            "type": "PersonalTask",
            "task_number": task_number
        }
        self.task_management.add_task(PersonalTask(**task_data))
        print("Personal task added successfully!")

    def create_work_task_from_input(self):
        name = input("Enter task name: ")
        deadline = input("Enter task deadline (format: dd/mm/yyyy): ")
        priorities = ["low", "medium", "high", "urgent"]
        priority = priorities[self.get_user_choice(priorities) - 1]
        colors = ["red", "blue", "green", "yellow"]
        color = colors[self.get_user_choice(colors) - 1]
        task_number = len([task for task in self.task_management.tasks if isinstance(task, WorkTask)]) + 1
        task_data = {
            "name": name,
            "deadline": deadline,
            "priority": priority,
            "color": color,
            "task_status": "pending",
            "type": "WorkTask",
            "task_number": task_number
        }
        self.task_management.add_task(WorkTask(**task_data))
        print("Work task added successfully!")

    def add_note_to_task(self):
        task_name = input("Enter the name of the task to add a note: ")
        note = input("Enter the note: ")
        for task in self.task_management.tasks:
            if task.name == task_name:
                task.add_note(note)
                print("Note added successfully!")
                break
        else:
            print(f"Task '{task_name}' not found.")

def display_menu():
    print("1- Add Personal Task")
    print("2- Add Work Task")
    print("3- Mark a Task as Completed")
    print("4- Get Task Status")
    print("5- List All Tasks")
    print("6- List Pending Tasks")
    print("7- Save Tasks to JSON")
    print("8- Edit Task")
    print("9- Add Note to Task")
    print("10- Delete a Task")
    print("11- Exit")

def main():
    task_management = TaskManagement()
    task_management.load_from_json()
    task_scheduling = TaskScheduling(task_management)

    while True:
        display_menu()
        choice = input("Enter your choice (1-10): ")
        if choice == "1":
            task_scheduling.create_personal_task_from_input()
        elif choice == "2":
            task_scheduling.create_work_task_from_input()
        elif choice == "3":
            task_name = input("Enter the name of the task to mark as completed: ")
            task_management.mark_task_completed(task_name)
        elif choice == "4":
            task_name = input("Enter the name of the task to get its status: ")
            status = task_management.get_task_status(task_name)
            if status is not None:
                print(f"Task '{task_name}' status: {'Completed' if status == 'completed' else 'Not Completed'}")
        elif choice == "5":
            task_management.print_tasks()
        elif choice == "6":
            task_management.print_pending_tasks()
        elif choice == "7":
            task_management.save_to_json()
            print("Tasks saved to JSON successfully!")
        elif choice == "8":
            task_editing = TaskEditing(task_management)
            task_editing.edit_task()
        elif choice == "9":
            task_scheduling.add_note_to_task()
        elif choice == "10":
            task_editing = TaskEditing(task_management)
            task_editing.delete_task()
        elif choice == "11":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()
