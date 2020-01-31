function registerToggle() {
    var items = document.getElementsByClassName("toggle-item");
    Array.prototype.forEach.call(items, item => {
        item.addEventListener('change', e => {
            // redirect the window to the redirect url
            // as held in the value.
            window.location.href = e.target.value;
        });
    });
}

window.onload = function() {
    this.registerToggle();
}
