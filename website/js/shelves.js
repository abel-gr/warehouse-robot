import { firebase } from './firebase.js';

var totalShelves = 72;
var shelvesPerRow = 6;
var shelvesPerCorridor = 3;

const e1 = "#42f56f";
const e2 = "#ebcc42";
const e3 = "#eb9742";
const e4 = "#eb4842";
const e5 = "#962a2a";

var shelve_buttons = [];
var shelve_states = [];
var shelve_orders = [];
var shelve_stocks = [];
var shelve_orders_data = [];

function getRealShelveState(id){
    return shelve_states[id];
}

function getRealInCompleteOrders(id){
    return shelve_orders[id];
}

function getRealStock(id){
    return shelve_stocks[id];
}

function getColorByState(state){
    switch (state){
        case 0:
            return e1;
        case 1:
            return e2;
        case 2:
            return e3;
        case 3:
            return e4;
        case 4:
            return e5;
    }
}

function calculateState(incomplete_orders, stock){
    var state = 0;

    if (incomplete_orders > stock){
        state = 4;
    }
    else if(stock === 0){
        state = 3;
    }
    else if (incomplete_orders <= stock && incomplete_orders >= (stock*0.5)){
        state = 2;
    }
    else if (incomplete_orders > 0){
        state = 1;
    }
    else{
        state = 0;
    }

    return state;
}

function getOrderGeneralInfo(id, incomplete_orders, orderState){
    return "Shelf ID: " + id + " - Orders: " + incomplete_orders + " - State: " + orderState;
}

function getShelveDatabaseData(){
    var dbRef = firebase.database().ref();

    dbRef.child("shelves/sections").child("section1").child("shelf1").get().then((snapshot) => {
        if (snapshot.exists()) {
            console.log(snapshot.val());
        } else {
            console.log("No data available");
        }
    }).catch((error) => {
        console.error(error);
    });

    for (var i = 0; i < totalShelves; i++) {

                //TODO: obtener las 3 variables de la DB
        var incomplete_orders = 0;
        if (Math.random() > 0.8) {
            incomplete_orders = Math.floor(Math.random() * 10);
        }
        var stock = Math.floor(Math.random() * 15);
        var orderState = 0;

        // TODO: obtener info pedidos de la DB
        if(incomplete_orders>0) {
            new_orders = [i, getOrderGeneralInfo(i, incomplete_orders, orderState)];
        }else{
            new_orders = "0";
        }
        /*new_orders = [];
        for(var j=0; j < incomplete_orders; j++){
            new_orders.push(j);
        }*/

        shelve_orders_data.push(new_orders)

        var state = calculateState(incomplete_orders, stock);
        shelve_states.push(state);
        shelve_orders.push(incomplete_orders);
        shelve_stocks.push(stock);
    }
}

function addShelve(id, container, state, incomplete_orders, stock) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "estanteria";
    button.name = id;
    button.id = "shelvesMapButton" + id;
    button.style.backgroundColor = getColorByState(state);

    button.innerHTML = incomplete_orders + "-" + stock;

    container.appendChild(button);

    shelve_buttons.push(button);
}

getShelveDatabaseData();

var rows = totalShelves/shelvesPerRow/shelvesPerCorridor;
var id = 0;
var shelves_per_section = shelvesPerRow * shelvesPerCorridor;
var shelve_sections = totalShelves / shelves_per_section;


for (var i = 0; i < rows; i++) {

    for(var k=0; k < shelvesPerCorridor; k++) {

        var sub_container = document.createElement("div");
        sub_container.type = "div";
        sub_container.className = "sub_container_shelves";

        document.getElementById("container_shelves").appendChild(sub_container);

        for (var j = 0; j < shelvesPerRow; j++) {
            addShelve(id, sub_container, getRealShelveState(id), getRealInCompleteOrders(id), getRealStock(id));
            id++;
        }
    }

    var horizontal_corridor = document.createElement("div");
    horizontal_corridor.type = "div";
    horizontal_corridor.className = "horizontal_corridor";
    document.getElementById("container_shelves").appendChild(horizontal_corridor);


}
