
function saveVoiceOrderToDB(shelfID, quantity){
    addOrderWithQuantity(shelfID, -1, -1, quantity);
    //window.alert('Your order has been sent!');
}