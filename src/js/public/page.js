const { $ } = mdui;

document.addEventListener('DOMContentLoaded', function () {

    const search = new URLSearchParams(window.location.search);
    const path = searchParams.get('path');

    if (!path) {
        return;
    }
    else {
        $.ajax({
            method: 'GET',
            url: "/page/blog/md/" + encodeURIComponent(path),
        }).then((res) => {
            console.log("res");
            marked.setOptions({
                gfm: true,
                breaks: true,
                pedantic: false,
                sanitize: false,
            });
            document.querySelector("#md_content").innerHTML = marked.parse(res);
        }).catch((error) => {
            console.log(error);
        });
    }

});