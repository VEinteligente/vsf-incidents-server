var edit_record;
var csrftoken = getCookie('csrftoken');

// Configuración de las llamadas AJAX.
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$('.add-fam-rec').click(function(){
    var elem = $(this);
    // Se limpia el formulario
    $('#form-fam-rec').find('input').val("");
    $('#fam-rec-label').html('Agregar antecedente');
    $('#btn-sbt-fam-rec').html('Agregar');
    $('#modal-fam-rec').modal('show');
});

$('.edit-fam-rec').click(editFamilyRecordButton);

function editFamilyRecordButton(){
    var elem = $(this);
    edit_record = elem.parents('tr');
    // Se limpia el formulario
    $('#form-fam-rec').find('input').val("");

    $('#id_old_relative').val(edit_record.find('.fam-rec-rel').data('rel'));
    $('#id_relative').val(edit_record.find('.fam-rec-rel').data('rel'));
    $('#id_old_status').val(edit_record.find('.fam-rec-stat').data('stat'));
    $('#id_status').val(edit_record.find('.fam-rec-stat').data('stat'));
    $('#id_old_age').val(edit_record.find('.fam-rec-age').html());
    $('#id_age').val(edit_record.find('.fam-rec-age').html());
    $('#form-fam-rec #id_old_category').val(edit_record.find('.fam-rec-cat').html());
    $('#form-fam-rec #id_category').val(edit_record.find('.fam-rec-cat').html());
    $('#form-fam-rec #id_old_record').val(edit_record.find('.fam-rec-rec').html());
    $('#form-fam-rec #id_record').val(edit_record.find('.fam-rec-rec').html());
    $('#fam-rec-label').html('Editar antecedente');
    $('#btn-sbt-fam-rec').html('Editar');
    $('#modal-fam-rec').modal('show');
}

$('.del-fam-rec').click(delFamilyRecordButton);

function delFamilyRecordButton(){
    var elem = $(this);
    edit_record = elem.parents('tr');
    // Se limpia el formulario
    $('#form-fam-rec #id_category').val(edit_record.find('.fam-rec-cat').html());
    $('#form-fam-rec #id_record').val(edit_record.find('.fam-rec-rec').html());
    var r = confirm("¿Está seguro que desa eliminar el antecedente?");
    if (r == true) {
        $.ajax({
            url: urlFamilyRecord,
            data: $('#form-fam-rec').serialize(),
            method: "DELETE",
        }).done(function(){
            edit_record.remove();
        }).fail(function(){
            alert('Hubo un problema con la conexión con el servidor. Por favor intente más tarde.');
            $('#modal-fam-rec').modal('hide');
        });
    };
}


$(document).ready(function(){
    $('#modal-fam-rec').modal({show: false});

    // Inicializar los autocompletes
    $('#form-fam-rec #id_category').autocomplete({
        source: urlPersonalRecordCategoriesList + "&familiar=True",
        open: function(event, ui) {
            $(".ui-autocomplete").css("z-index", 2000);
        }
    });
    $('#form-fam-rec #id_record').autocomplete({
        source: urlPersonalRecordRecordsList,
        open: function(event, ui) {
            $(".ui-autocomplete").css("z-index", 2000);
        }
    });
});

function sendFamilyRecordForm(ajaxMethod, formSuccess){
    $('#form-fam-rec').validator('validate');
    if ($('#form-fam-rec .has-error').length > 0){
        return false;
    };
    $.ajax({
        url: urlFamilyRecord,
        data: $('#form-fam-rec').serialize(),
        method: ajaxMethod,
    }).done(formSuccess).fail(function(){
        alert('Hubo un problema con la conexión con el servidor. Por favor intente más tarde.');
        $('#modal-fam-rec').modal('hide');
    });
};


function createFamilyRecordSuccess(data){
    var new_elem = "<tr>";
    new_elem += "<td class='fam-rec-rel' data-rel='" + data["relative"] + "'>" + data["relative_display"] + "</td>";
    new_elem += "<td class='fam-rec-stat' data-stat='" + data["status"] + "'>" + data["status_display"] + "</td>";
    new_elem += "<td class='fam-rec-age'>" + data["age"] + "</td>";
    new_elem += "<td class='fam-rec-cat'>" + data["category"] + "</td>";
    if (data["record"]) {
        new_elem += "<td class='fam-rec-rec'>" + data["record"] + "</td>";
    } else {
        new_elem += "<td class='fam-rec-rec'></td>";
    }
    new_elem += '<td>';
    new_elem += '<button type="button" class="btn btn-warning btn-sm edit-fam-rec">Editar</button>';
    new_elem += '<button type="button" class="btn btn-danger btn-sm del-fam-rec">Eliminar</button>';
    new_elem += '</td>';
    new_elem += '</tr>';
    $('#fam-rec-body').append(new_elem);
    $('.edit-fam-rec').click(editFamilyRecordButton);
    $('.del-fam-rec').click(delFamilyRecordButton);
    $('#modal-fam-rec').modal('hide');
}

function editFamilyRecordSuccess(data){
    edit_record.find('.fam-rec-rel').data('rel', data["relative"]);
    edit_record.find('.fam-rec-rel').html(data["relative_display"]);
    edit_record.find('.fam-rec-stat').data('stat', data["status"]);
    edit_record.find('.fam-rec-stat').html(data["status_display"]);
    edit_record.find('.fam-rec-age').html(data["age"]);
    edit_record.find('.fam-rec-cat').html(data["category"]);
    edit_record.find('.fam-rec-rec').html(data["record"]);
    $('#modal-fam-rec').modal('hide');
}

$('#form-fam-rec').submit(function(event){
    event.preventDefault();
    if ($('#form-fam-rec #id_old_record').val() === "") {
        sendFamilyRecordForm("POST", createFamilyRecordSuccess)
    } else {
        sendFamilyRecordForm("PUT", editFamilyRecordSuccess)
    }
});

// Función para settear url de búsqueda de los records
$('#form-fam-rec #id_category').blur(function(){
    var urlR = urlFamilyRecordRecordsList + '?category=' + $('#form-fam-rec #id_category').val();
    $("#id_record").autocomplete("option", "source", urlR);
});
