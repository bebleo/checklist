// check that jQuery has loaded and if not load from the local source.
window.jQuery || document.write('<script src="/static/js/jquery-min.3.4.1.min.js">\x3c</script>');

$(".toggle-item").change(function(e) {
    window.location.href = e.target.value;
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
