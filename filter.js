var selector = document.querySelector('#filterStateAnchor');
if (selector) selector.click();

setTimeout(() => {{

    // 先清除默认选中
    document.querySelectorAll('input[id^="country"]').forEach(cb => cb.checked = false);

    // 选择国家
    const countryCheckboxes = document.querySelectorAll('input[id^="country"]');
    countryCheckboxes.forEach(cb => {{
        const id = cb.id.replace('country', '');
        if (["37", "25", "6", "35", "5", "72"].includes(id)) {{
            cb.checked = true;
        }}
    }});

    // 选择种类
    // TODO
    // 选择重要程度
    // TODO
    // 点击应用
    const submit_btn = document.querySelector('#ecSubmitButton');
    submit_btn.click();

}}, 1000);  //给1秒等待过滤器面板展开