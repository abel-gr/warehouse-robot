
function getShelveInfo(id){
    return [shelve_orders[id], shelve_stocks[id]];
}

var lastS = "";

$('.estanteria').mouseenter(function(e) {

    if($(this).attr("name")!==lastS){
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