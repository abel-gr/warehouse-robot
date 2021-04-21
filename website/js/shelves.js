
var totalShelves = 96;
var shelvesPerRow = 6;
var shelvesPerCorridor = 4;

function getShelveDatabaseData(){
    for (var i = 0; i < totalShelves; i++) {
        //TODO: obtener las 3 variables de la DB

        var state = 0;//Math.floor(Math.random() * 4);
        var incomplete_orders = Math.floor(Math.random() * 100);
        var stock = Math.floor(Math.random() * 100);

        if (incomplete_orders > stock){
            state = 4;
        }
        else if(stock === 0){
            state = 3;
        }
        else if (incomplete_orders < stock && incomplete_orders >= (stock*0.5)){
            state = 2;
        }
        else if (incomplete_orders > 0){
            state = 1;
        }
        else{
            state = 0;
        }

        shelve_states.push(state);
        shelve_orders.push(incomplete_orders);
        shelve_stocks.push(stock);
    }
}

function getRealShelveState(id){
    return shelve_states[id];
}

function getRealInCompleteOrders(id){
    return shelve_orders[id];
}

function getRealStock(id){
    return shelve_stocks[id];
}

const e1 = "#42f56f";
const e2 = "#ebcc42";
const e3 = "#eb9742";
const e4 = "#eb4842";
const e5 = "#962a2a";

var shelve_buttons = [];
var shelve_states = [];
var shelve_orders = [];
var shelve_stocks = [];

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

function addShelve(id, container, state, incomplete_orders, stock) {
    var button = document.createElement("button");
    button.type = "button";
    button.className = "estanteria";
    button.name = id;
    button.style.backgroundColor = getColorByState(state);
    button.onclick = function() { checkShelve(id); };

    button.innerHTML = incomplete_orders + "-" + stock;

    container.appendChild(button);

    shelve_buttons.push(button);
}

getShelveDatabaseData();

var rows = totalShelves/shelvesPerRow/shelvesPerCorridor;
var id = 0;

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
