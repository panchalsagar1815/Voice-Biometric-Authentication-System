import os
import pickle
import shutil
from glob import glob
from main_functions import *

# deletes a registered user from database
def delete_user():

    speak("Enter name of the user")
    name = input("Enter name of the user: ")

    with open("./User_db/embedding.pickle", "rb") as database:
        db = pickle.load(database)
    # print(type(db))


    # print(user)

    if name in db:
        db.remove(name)

        # save the database
        with open('User_db/embedding.pickle', 'wb') as database:
            pickle.dump(db, database, protocol=pickle.HIGHEST_PROTOCOL)

        [os.remove(path) for path in glob('./voice_database/' + name + '/*.wav')]
        [os.remove(path) for path in glob('./voice_database/' + name + '/*.txt')]
        [shutil.rmtree(path) for path in glob('./voice_database/' + name + '/*')]
        shutil.rmtree('./voice_database/' + name)
        os.remove('./gmm_models/' + name + '.gmm')

        print('User ' + name + ' deleted successfully')
        msg = 'User ' + name + ' deleted successfully'
        speak(msg)

    else:
        # speak('No such user !!')
        print('No such user !!')
        speak('No such user !!')


if __name__ == '__main__':
    delete_user()