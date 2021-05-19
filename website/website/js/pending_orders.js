
var sectionOrders = [];

function generateListItemOrder(sectionid, shelfID, info){
    var elemento = document.createElement("li");
    elemento.type = "li";
    elemento.className = "list-group-item";

    elemento.id = "shelf_orders_list_info_general_" + shelfID;
    elemento.innerHTML = info;

    return elemento;
}

function getOrdersListItems(sectionid){
    var listado = document.createElement("ul");
    listado.type = "ul";
    listado.className = "list-group list-group-flush";
    listado.id = "section_ul_" + sectionid;

    for(var i=0; i<sectionOrders[sectionid].length;i++) {
        var shelfID = sectionOrders[sectionid][i][0];
        var info = sectionOrders[sectionid][i][1];

        var elemento = generateListItemOrder(sectionid, shelfID, info);

        listado.appendChild(elemento);
    }

    return listado;
}

function addOrdersSections(){
    var parent = $("#list_items_orders");

    parent.html("");

    for(var sectionID = 0; sectionID < shelve_sections; sectionID++) {
        var template = $('#order_section_template').clone();

        var title = template.find(".card-title");
        var idheading = "collapseheading" + sectionID;
        title.attr("id", idheading);

        var butt = template.find("button");
        var idcollapse = "collapse" + sectionID;

        butt.attr("data-target", "#collapse" + sectionID);
        butt.attr("aria-controls", idcollapse);
        butt.html("Section " + sectionID);

        var coll = template.find(".collapse");
        coll.attr("aria-labelledby", idheading);
        coll.attr("id", idcollapse);

        var body = template.find(".card-body");
        body.html(getOrdersListItems(sectionID));

        template.css("display", "block");
        parent.append(template);
    }
}

function getAllOrders(){

    var shelve_id = 0;
    sectionOrders = [];

    for(var sectionID = 0; sectionID < shelve_sections; sectionID++) {
        var orders = [];

        for(var i = 0; i < shelves_per_section; i++) {
            if (typeof shelve_orders_data[shelve_id] !== 'string' && !(shelve_orders_data[shelve_id] instanceof String)){
                if(shelve_orders_data[shelve_id] !== undefined) {
                    orders.push(shelve_orders_data[shelve_id]);
                }
            }
            shelve_id++;
        }

        sectionOrders.push(orders); // This adds the list of orders that are from that section

    }
}

getAllOrders();
addOrdersSections();
