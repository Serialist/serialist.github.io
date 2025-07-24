const { $ } = mdui;

document.addEventListener('DOMContentLoaded', function () {
    if (window.location.pathname == "/page/blog/" || window.location.pathname == "/page/blog/index.html") {
        $.ajax({
            method: 'GET',
            url: '/page/blog/md/index.json',
        }).then((res) => {
            console.log("blog list get successful");
            const list = document.querySelector("#blog_list");
            for (const [title, { path }] of Object.entries(res)) {
                const item = document.createElement('mdui-list-item');
                item.setAttribute('href', "/page/blog/blog.html?path=" + encodeURIComponent(path));
                item.textContent = title;
                list.appendChild(item);
            }
        }).catch((error) => {
            console.log(error);
        });
    }
});
