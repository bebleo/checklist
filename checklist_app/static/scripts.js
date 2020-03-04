$(".toggle-item").change(function(e) {
    window.location.href = e.target.value
});

$(".inactive").hide();
$(".edit_item_links").hide();

$(".list_item").hover( 
    function() {
        $(this).children(".edit_item_links").fadeIn();
    },
    function() {
        $(this).children(".edit_item_links").hide();
    }
);
