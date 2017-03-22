var edit_habit;
var csrftoken = getCookie('csrftoken');

// Configuración de las llamadas AJAX.
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$('.add-habit').click(function(){
    var elem = $(this);
    // Se limpia el formulario
    $('#form-habit').find('input').val("");
    $('#habit-label').html('Agregar hábito');
    $('#btn-sbt-habit').html('Agregar');
    $('#modal-habit').modal('show');
});

$('.edit-habit').click(editHabitButton);

function editHabitButton(){
    var elem = $(this);
    edit_habit = elem.parents('tr');
    // Se limpia el formulario
    $('#form-habit').find('input').val("");
    $('#id_old_habit').val(edit_habit.find('.habit-name').html());
    $('#id_habit').val(edit_habit.find('.habit-name').html());
    $('#id_old_comment').val(edit_habit.find('.habit-comment').html());
    $('#id_comment').val(edit_habit.find('.habit-comment').html());
    $('#habit-label').html('Editar hábito');
    $('#btn-sbt-habit').html('Editar');
    $('#modal-habit').modal('show');
}

$('.del-habit').click(delHabitButton);

function delHabitButton(){
    var elem = $(this);
    edit_habit = elem.parents('tr');
    // Se limpia el formulario
    $('#id_habit').val(edit_habit.find('.habit-name').html());
    $('#id_comment').val(edit_habit.find('.habit-comment').html());
    var r = confirm("¿Está seguro que desa eliminar el hábito?");
    if (r == true) {
        $.ajax({
            url: urlHabits,
            data: $('#form-habit').serialize(),
            method: "DELETE",
        }).done(function(){
            edit_habit.remove();
        }).fail(function(){
            alert('Hubo un problema con la conexión con el servidor. Por favor intente más tarde.');
            $('#modal-habit').modal('hide');
        });
    };
}


$(document).ready(function(){
    $('#modal-habit').modal({show: false});

    // Inicializar los autocompletes
    $('#id_habit').autocomplete({
        source: urlHabitsListAPI,
        open: function(event, ui) {
            $(".ui-autocomplete").css("z-index", 2000);
        }
    });
});

function sendHabitForm(ajaxMethod, formSuccess){
    $('#form-sub').validator('validate');
    if ($('.has-error').length > 0){
        return false;
    };
    $.ajax({
        url: urlHabits,
        data: $('#form-habit').serialize(),
        method: ajaxMethod,
    }).done(formSuccess).fail(function(){
        alert('Hubo un problema con la conexión con el servidor. Por favor intente más tarde.');
        $('#modal-habit').modal('hide');
    });
};


function createHabitSuccess(data){
    var new_elem = "<tr>";
    new_elem += "<td class='habit-name'>" + data["habit"] + "</td>";
    if (data["comment"]) {
        new_elem += "<td class='habit-comment'>" + data["comment"] + "</td>";
    } else {
        new_elem += "<td class='habit-comment'></td>";
    }
    new_elem += '<td>';
    new_elem += '<button type="button" class="btn btn-warning btn-sm edit-habit">Editar</button>';
    new_elem += '<button type="button" class="btn btn-danger btn-sm del-habit">Eliminar</button>';
    new_elem += '</td>';
    new_elem += '</tr>';
    $('#habit-body').append(new_elem);
    $('.edit-habit').click(editHabitButton);
    $('.del-habit').click(delHabitButton);
    $('#modal-habit').modal('hide');
}

function editHabitSuccess(data){
    edit_habit.find('.habit-name').html(data["habit"]);
    edit_habit.find('.habit-comment').html(data["comment"]);
    $('#modal-habit').modal('hide');
}

$('#form-habit').submit(function(event){
    event.preventDefault();
    if ($('#id_old_habit').val() === "") {
        sendHabitForm("POST", createHabitSuccess)
    } else {
        sendHabitForm("PUT", editHabitSuccess)
    }
});
