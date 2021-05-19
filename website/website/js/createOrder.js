

function saveOrderToDB(data){
    // TODO: Guardar el nuevo pedido en la base de datos
}

function calculateSectionIDByShelfID(id){
    return Math.floor(id/shelves_per_section);
}

function addOrder(data){
    var id = data["shelfID"];
    var destinationID = data["destinationID"];
    var productID = data["productID"];

    shelve_orders[id] = shelve_orders[id] + 1;

    var incomplete_orders = shelve_orders[id];
    var stock = shelve_stocks[id];

    $("#shelvesMapButton" + id).html(incomplete_orders + "-" + stock);

    $("#shelveInfoID").html(id);
    $("#shelveInfoOrders").html(incomplete_orders);
    $("#shelveInfoStock").html(stock);

    $("#shelveInfo").fadeIn(50);

    $(".estanteria").removeClass("estanteria_seleccionada");
    $("#shelvesMapButton" + id).addClass("estanteria_seleccionada");

    var state = calculateState(incomplete_orders, stock);
    $("#shelvesMapButton" + id).css("backgroundColor", getColorByState(state));

    var orderState = 0;
    var info = getOrderGeneralInfo(id, incomplete_orders, orderState);
    var order_list_item = $("#shelf_orders_list_info_general_" + id);

    if(order_list_item.length) {
        order_list_item.html(info);
    }else{
        var sectionid = calculateSectionIDByShelfID(id);
        var elemento = generateListItemOrder(sectionid, id, info);

        $("#section_ul_" + sectionid).append(elemento);
    }

    saveOrderToDB(data);
}


$("#buttonCreateOrderSubmit").click(function(event){
    event.preventDefault();

    // Code from Bootstrap documentation: https://getbootstrap.com/docs/4.0/components/forms/
    var forms = document.getElementsByClassName('needs-validation');
        var validation = Array.prototype.filter.call(forms, function(form) {

            form.classList.add('was-validated');

            if (form.checkValidity() === false) {
                event.preventDefault();
                event.stopPropagation();
            } else {

                $("#createOrderModal").modal('toggle');

                var dataForm = {};

                var shelfid = $("#valueShelfID_createorderform").val();
                dataForm["shelfID"] = shelfid;

                var destinationID = $("#valueDestinationID_createorderform").val();
                dataForm["destinationID"] = destinationID;

                var ProductID = $("#valueProductID_createorderform").val();
                dataForm["productID"] = ProductID;

                addOrder(dataForm);

            }
    });

});