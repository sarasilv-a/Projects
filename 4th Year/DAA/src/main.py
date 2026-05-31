import utils as u

training_path = 'Datasets/training_data.csv'
testing_path = 'Datasets/test_data.csv'

def options_treatment():
    print('Choose the preferred data treatment method:')
    print('1. Method A')
    print('2. Method B')
    print('3. Method C')
    opt = input('Enter the number of your choice: ')
    return opt
 
def options_modeling():
    print('Choose the preferred modeling method:')
    print('1. Model X')
    print('2. Model Y')
    print('3. Model Z')
    opt = input('Enter the number of your choice: ')
    return opt

# ========================
# ========= MAIN =========
if __name__ == '__main__':
    print('=============== DAA PROJECT ===============')
    print()
    
    training_data = u.load_data(training_path)

    choice = options_treatment()
    if choice == '1':
        print('Method A')
    elif choice == '2':
        print('Method B')
    elif choice == '3':
        print('Method C')
    else:
        print('Invalid choice')

    print()

    choice = options_modeling()
    if choice == '1':
        print('Model X')
    elif choice == '2':
        print('Model Y')
    elif choice == '3':
        print('Model Z')
    else:
        print('Invalid choice')

    print()