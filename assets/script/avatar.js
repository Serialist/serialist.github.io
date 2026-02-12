
function Avatar_Link(name, site_url, avatar_url) {
    return `
        <mdui-card href="${site_url}" target="_blank" style="width: 10em; height: 10em; position: relative; padding: 0; overflow: hidden;">
            <img src="${avatar_url}" alt="${name}" style="width: 10em; height: 10em; object-fit: cover;">
            <span style="position: absolute; bottom: 0; left: 0; width: 100%; background: rgba(255, 255, 255, 0.781); color: #000; text-align: center; padding: 0.3em 0; font-size: 1em;">${name}</span>
        </mdui-card>
    `;
}
