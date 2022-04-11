$(document).ready(function () {
    $('.Amount-remove').on('click', function () {
        let shop_product_id = $(this.parentElement).attr('shop_product_id')
        url_cart = $(this.parentElement).attr('href')
        let data = {
            shop_product_id: shop_product_id,
            action: 'remove'
        }

        let count = parseInt($(`.Amount-input[shop_product_id="${shop_product_id}"]`).attr('value'))

        if (count !== 0) {
            $(`.Amount-input[shop_product_id="${shop_product_id}"]`).attr('value', `${count - 1}`)
            if ($(`.error[shop_product_id="${shop_product_id}"]`).text() === 'Недостаточно товара') {
                $(`.error[shop_product_id="${shop_product_id}"]`).text('')
            } else {
                change_count(data, url_cart)
            }

        }
    });

    $('.Amount-add').on('click', function () {
        let shop_product_id = $(this.parentElement).attr('shop_product_id')
        url_cart = $(this.parentElement).attr('href')
        let data = {
            shop_product_id: shop_product_id,
            action: 'add'
        }
        let count = parseInt($(`.Amount-input[shop_product_id="${shop_product_id}"]`).attr('value'))
        $(`.Amount-input[shop_product_id="${shop_product_id}"]`).attr('value', `${count + 1}`)

        change_count(data, url_cart)
    });

    function change_count(params, url_cart) {
        var csrftoken = getCookie('csrftoken');
        $.ajax({
            method: "GET",
            dataType: "json",
            data: params,
            url: url_cart,
            headers: {'X-CSRFToken': csrftoken},
            success: function (data) {
                let shop_product_id = params['shop_product_id']
                if (data['error'] === 'Недостаточно товара') {
                    $(`.error[shop_product_id="${shop_product_id}"]`).text('Недостаточно товара')
                    alert('Недостаточно товара')
                    $(`.Amount-remove[shop_product_id="${shop_product_id}"]`).trigger("click")
                } else {
                    $("#total_price_cart").text(data['total_price'] + 'руб.')
                    $(".CartBlock-price").text(data['total_price'] + 'руб.')
                    $("#number_of_goods").text(data['quantity'])
                }
            }
        })
    };

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
