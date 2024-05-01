import firebase_admin

from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate('/Users/davidhorobet/PhytonProjects/face-firebase/facerecognitionsystem-ceca6-firebase-adminsdk-z7cct-37fae0dd96.json')

firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://facerecognitionsystem-ceca6-default-rtdb.firebaseio.com/'
})

ref = db.reference('py/')
user_ref = ref.child('users')
user_ref.set({
    'david': {
        'clock in' : 'June 23, 13:40',
        'full_name' : 'David Horobet'
    },
     'marian':{
        'clock in' : 'June 25, 12:40',
        'full_name' : 'marina apostol'
    },
})

