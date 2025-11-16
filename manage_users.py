"""
User and Child Management CLI
Simple interface to create users, add children, and set active child
"""

import sys
from pathlib import Path
from user_child_manager import UserChildManager

def print_menu():
    print("\n" + "="*70)
    print(" User & Child Management ".center(70))
    print("="*70)
    print("\n1. Create new user")
    print("2. Add child to current user")
    print("3. List all users")
    print("4. List all children")
    print("5. Set current user")
    print("6. Set current child")
    print("7. Show current user/child")
    print("8. Exit")
    print("\n" + "="*70)

def main():
    manager = UserChildManager()
    
    # Show current setup
    current_user = manager.get_current_user()
    current_child = manager.get_current_child()
    
    if current_user and current_child:
        print(f"\nCurrent User: {current_user['name']} ({current_user['email']})")
        print(f"Current Child: {current_child['name']} (ID: {current_child['childId']})")
    else:
        print("\nNo user/child set. Creating defaults...")
        manager.ensure_default_setup()
        current_user = manager.get_current_user()
        current_child = manager.get_current_child()
        print(f"Created default user: {current_user['name']}")
        print(f"Created default child: {current_child['name']}")
    
    while True:
        print_menu()
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == '1':
            name = input("Enter user name: ").strip()
            email = input("Enter email: ").strip()
            if name and email:
                user = manager.create_user(name, email)
                print(f"\n✅ User created: {user['name']} (ID: {user['userId']})")
                set_current = input("Set as current user? (y/n): ").strip().lower()
                if set_current == 'y':
                    manager.set_current_user(user['userId'])
                    print("✅ Set as current user")
            else:
                print("❌ Name and email required")
        
        elif choice == '2':
            current_user = manager.get_current_user()
            if not current_user:
                print("❌ No current user. Please set a user first.")
                continue
            
            name = input("Enter child name: ").strip()
            age_str = input("Enter child age (optional): ").strip()
            age = int(age_str) if age_str.isdigit() else None
            
            if name:
                child = manager.create_child(current_user['userId'], name, age)
                print(f"\n✅ Child created: {child['name']} (ID: {child['childId']})")
                set_current = input("Set as current child? (y/n): ").strip().lower()
                if set_current == 'y':
                    manager.set_current_child(child['childId'])
                    print("✅ Set as current child")
            else:
                print("❌ Child name required")
        
        elif choice == '3':
            users = manager.load_users()
            print("\nAll Users:")
            print("-" * 70)
            for user in users:
                current_marker = " (CURRENT)" if current_user and user['userId'] == current_user['userId'] else ""
                print(f"  {user['name']} ({user['email']}) - ID: {user['userId']}{current_marker}")
                print(f"    Children: {len(user.get('children', []))}")
        
        elif choice == '4':
            children = manager.load_children()
            print("\nAll Children:")
            print("-" * 70)
            for child in children:
                current_marker = " (CURRENT)" if current_child and child['childId'] == current_child['childId'] else ""
                age_str = f", Age: {child['age']}" if child.get('age') else ""
                print(f"  {child['name']}{age_str} - ID: {child['childId']}{current_marker}")
                print(f"    User: {child['userId']}")
        
        elif choice == '5':
            users = manager.load_users()
            if not users:
                print("❌ No users found. Create a user first.")
                continue
            
            print("\nAvailable Users:")
            for i, user in enumerate(users, 1):
                print(f"  {i}. {user['name']} ({user['email']}) - ID: {user['userId']}")
            
            try:
                idx = int(input("\nEnter user number: ").strip()) - 1
                if 0 <= idx < len(users):
                    manager.set_current_user(users[idx]['userId'])
                    print(f"✅ Set {users[idx]['name']} as current user")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '6':
            current_user = manager.get_current_user()
            if not current_user:
                print("❌ No current user. Please set a user first.")
                continue
            
            children = manager.get_children_for_user(current_user['userId'])
            if not children:
                print("❌ No children found for current user. Add a child first.")
                continue
            
            print(f"\nChildren for {current_user['name']}:")
            for i, child in enumerate(children, 1):
                age_str = f", Age: {child['age']}" if child.get('age') else ""
                print(f"  {i}. {child['name']}{age_str} - ID: {child['childId']}")
            
            try:
                idx = int(input("\nEnter child number: ").strip()) - 1
                if 0 <= idx < len(children):
                    manager.set_current_child(children[idx]['childId'])
                    print(f"✅ Set {children[idx]['name']} as current child")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == '7':
            current_user = manager.get_current_user()
            current_child = manager.get_current_child()
            
            print("\nCurrent Setup:")
            print("-" * 70)
            if current_user:
                print(f"User: {current_user['name']} ({current_user['email']})")
                print(f"  ID: {current_user['userId']}")
                print(f"  Children: {len(current_user.get('children', []))}")
            else:
                print("User: None")
            
            if current_child:
                age_str = f", Age: {current_child['age']}" if current_child.get('age') else ""
                print(f"\nChild: {current_child['name']}{age_str}")
                print(f"  ID: {current_child['childId']}")
            else:
                print("\nChild: None")
        
        elif choice == '8':
            print("\n👋 Goodbye!\n")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


