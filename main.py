from database import connect, create_table

create_table()

def add_task(title, priority, due_date):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, status, priority, due_date) VALUES (?, ?, ?, ?)",
        (title, "Pending", priority, due_date)
    )
    conn.commit()
    conn.close()
    print("Task added successfully!")

def view_tasks():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()

    if not tasks:
        print("No tasks found.")
    else:
        print("\n--- Task List ---")
        for task in tasks:
            print(f"ID:{task[0]} | {task[1]} | {task[2]} | Priority:{task[3]} | Due:{task[4]}")

def filter_tasks(status):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE status=?", (status,))
    tasks = cursor.fetchall()
    conn.close()

    print(f"\n--- {status} Tasks ---")
    for task in tasks:
        print(task)

def update_task(task_id, status):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
    conn.commit()
    conn.close()
    print("Task updated!")

def delete_task(task_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    print("Task deleted!")


# Menu
while True:
    print("\n===== Task Manager =====")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Filter Tasks")
    print("6. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        title = input("Enter task: ")
        priority = input("Priority (High/Medium/Low): ")
        due_date = input("Due date (YYYY-MM-DD): ")
        add_task(title, priority, due_date)

    elif choice == "2":
        view_tasks()

    elif choice == "3":
        task_id = int(input("Enter task ID: "))
        status = input("Status (Pending/Done): ")
        update_task(task_id, status)

    elif choice == "4":
        task_id = int(input("Enter task ID: "))
        delete_task(task_id)

    elif choice == "5":
        status = input("Enter status to filter (Pending/Done): ")
        filter_tasks(status)

    elif choice == "6":
        break

    else:
        print("Invalid choice")