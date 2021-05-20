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

var rows = totalShelves/shelvesPerRow/shelvesPerCorridor;
var id = 0;
var shelves_per_section = shelvesPerRow * shelvesPerCorridor;
var shelve_sections = totalShelves / shelves_per_section;

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

function loadDatabaseDatainMap(sectionDataDB){
    var shelfID_a = "shelf";
    var sectionID_a = "section";

    var j = 1;
    var k = 1;

    shelve_states = [];
    shelve_orders = [];
    shelve_stocks = [];
    shelve_orders_data = [];

    for (var i = 0; i < totalShelves; i++) {

        var incomplete_orders;
        var orderState;
        var stock;

        if(sectionDataDB.length > 0) {

            incomplete_orders = sectionDataDB[0][sectionID_a + k.toString()][shelfID_a + j.toString()]["incomplete_orders"];
            orderState = sectionDataDB[0][sectionID_a + k.toString()][shelfID_a + j.toString()]["orderState"];
            stock = sectionDataDB[0][sectionID_a + k.toString()][shelfID_a + j.toString()]["stock"];

            //console.log(k, sectionID_a + k.toString(), shelfID_a + j.toString(), incomplete_orders, orderState, stock);

            if (j < shelves_per_section) {
                j++;
            } else {
                j = 1;
                k++;
            }

        }else {

            incomplete_orders = 0;
            if (Math.random() > 0.8) {
                incomplete_orders = Math.floor(Math.random() * 10);
            }
            stock = Math.floor(Math.random() * 15);
            orderState = 0;

        }

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

function loadInitialDataShelves()
{
    for (var i = 0; i < totalShelves; i++) {

        var incomplete_orders;
        var orderState;
        var stock;

        incomplete_orders = 0;
        if (Math.random() > 0.8) {
            incomplete_orders = Math.floor(Math.random() * 10);
        }
            stock = Math.floor(Math.random() * 15);
            orderState = 0;


        if(incomplete_orders>0) {
            new_orders = [i, getOrderGeneralInfo(i, incomplete_orders, orderState)];
        }else{
            new_orders = "0";
        }

        shelve_orders_data.push(new_orders)

        var state = calculateState(incomplete_orders, stock);
        shelve_states.push(state);
        shelve_orders.push(incomplete_orders);
        shelve_stocks.push(stock);
    }
}

function getShelveDatabaseData(){

    try {

        var dbRef = firebase.database().ref();

        dbRef.child("shelves/sections").get().then((snapshot) => {

            var sectionDataDB = [];

            if (snapshot.exists()) {
                console.log(snapshot.val());
                sectionDataDB.push(snapshot.val());

                loadDatabaseDatainMap(sectionDataDB);
                generateMap();

                getAllOrders();
                addOrdersSections();

            } else {
                console.log("No data available");
            }

        }).catch((error) => {
            console.error(error);
        });

    }catch(exception){

    }

    loadInitialDataShelves();
    generateMap();
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

function shelveListener() {

    $('.estanteria').mouseenter(function (e) {

        if ($(this).attr("name") !== lastS) {
            lastS = $(this).attr("name");

            var id = $(this).attr("name");
            info = getShelveInfo(parseInt(id));

            $("#shelveInfoID").html(id);
            $("#shelveInfoOrders").html(info[0]);
            $("#shelveInfoStock").html(info[1]);

            $("#shelveInfo").fadeIn(50);

            $(".estanteria").removeClass("estanteria_seleccionada");
            $(this).addClass("estanteria_seleccionada");
        }

    });

}

function generateMap(){

    $("#container_shelves").html("");

    shelve_buttons = [];

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

    shelveListener();
}

getShelveDatabaseData();
