import firebase from "firebase/app";
import "firebase/database";

var firebaseConfig = {
    apiKey: "AIzaSyCf0lFsEDrCVJ69hDs0CUt1XYsAnKYmMi4",
    authDomain: "warehousewaiter.firebaseapp.com",
    databaseURL: "https://warehousewaiter-default-rtdb.europe-west1.firebasedatabase.app",
    projectId: "warehousewaiter",
    storageBucket: "warehousewaiter.appspot.com",
    messagingSenderId: "218777444604",
    appId: "1:218777444604:web:4c055bcdd83c10c9117779",
    measurementId: "G-D6L3NYX1X9"
};
firebase.initializeApp(firebaseConfig);
firebase.analytics();

export {firebase};
