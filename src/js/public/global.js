
{
    var navigation_drawer = document.querySelector("mdui-navigation-drawer");
    document.querySelector("#menu_button").addEventListener("click", () => {
        navigation_drawer.open = !navigation_drawer.open;
    });
}
