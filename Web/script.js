// GENERAL

$('button').click(function() {
    $(this).parent().find('.toToggle').toggle();
});

// CATEGORIES

$.getJSON('reports/categories.json', function(data) {

    let items = [];

    $.each(data, function(key, value) {
        items.push(value);
        $('#selectCat').append('<option value="'+ value +'">'+ value +'</option>');
    });


});

// REPORT 1

$.getJSON('reports/report1.json', function(data) {
    let items = [];
    $.each(data, function(key, value) {
        items.push([value.country_name, value.count]);
        if(value.country_name != 'None') {
            $('.list#rep1').append('<div class="item"><b>'+ value.count +'</b> '+ value.country_name +'</div>');
        }   else {
            $('.list#rep1').append('<div class="item"><b>'+ value.count +'</b> <i>Unknown</i></div>');
        }
    });
});

// REPORT 2

function handleSecondReport(needleCategorie) {
    $.getJSON('reports/report2.json', function(data) {
        let items = [];

        $.each(data, function(key, value) {
            let item = {};
            item[key] = value;
            items.push(item);
        });

        found = false;
        let need = null;

        for(let i = 0; i < items.length; i++) {
            if(items[i][needleCategorie] != null) {
                need = items[i][needleCategorie];
                found = true;
                break;
            }
        }

        if(found) {
            $('.list#rep2').empty();

            $.each(need, function(key, value) {
                if(value[0] != 'None') {
                    $('.list#rep2').append('<div class="item"><b>'+ value[1] +'</b> '+ value[0] +'</div>');
                }   else {
                    $('.list#rep2').append('<div class="item"><b>'+ value[1] +'</b> <i>Unknown</i></div>');
                }
            });

            $('.toToggleRep2').show();
            $('#sRep2').text('Статистка по товарам из категории ' + needleCategorie + ':');
        }
    });
}

$('select').on('change', function() {
    handleSecondReport(this.value);
});

// REPORT 4

$.getJSON('reports/report4.json', function(data) {
    $('#sRep4').text(data.average_request_count);
});

