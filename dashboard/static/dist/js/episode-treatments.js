$('.add-tre').click(function(){
    edit_treatment = undefined;
    var elem = $(this);
    var form = $('#form-tre');
    // Se limpia el formulario
    form.find('input').val("");
    form.find('#id_date').val(moment().format('DD/MM/YYYY'))
    $('#tre-label').html('Agregar tratamiento');
    $('#btn-sbt-tre').html('Agregar');
    $('#modal-tre').modal('show');
});


function serializeTreatments() {
    var treats = [];
    $('.treatment').each(function(){
        var treat = {};
        treat["date"] =  moment($(this).find('.tre-date').html(), "DD/MM/YYYY").format('YYYY-MM-DD hh:mm');
        treat["treatment"] = $(this).find('.tre-tre').html();
        treat["comment"] = $(this).find('.tre-com').html();
        treats.push(treat);
    });
    return treats;
}

$('.edit-tre').click(TreatmentEditButton);

function TreatmentEditButton(){
    var elem = $(this);
    edit_treatment = elem.parents('tr');
    // Se limpia el formulario
    var form = $('#form-tre');
    form.find('#id_date').val(edit_treatment.find('.tre-date').html());
    form.find('#id_treatment').val(edit_treatment.find('.tre-tre').html());
    form.find('#id_comment').val(edit_treatment.find('.tre-com').html());
    $('#tre-label').html('Editar tratamiento');
    $('#btn-sbt-tre').html('Editar');
    $('#modal-tre').modal('show');
}

$('.del-tre').click(TreatmentDelButton);

function TreatmentDelButton(){
    var elem = $(this);
    edit_treatment = elem.parents('tr');
    
    var r = confirm("¿Está seguro que desa eliminar el tratamiento?");
    if (r == true) {
        edit_treatment.remove();
        saveEpisode();
    };
}


$(document).ready(function(){
    $('#modal-tre').modal({show: false});
    $('#id_treatment').autocomplete({
        source: urlTreatmentsList,
        open: function(event, ui) {
            $(".ui-autocomplete").css("z-index", 2000);
        }
    });

});


function TreatmentCreateSuccess(){
    var form = $('#form-tre');
    var new_elem = "<tr class='treatment'>";
    new_elem += "<td class='tre-date'>" + form.find('#id_date').val() + "</td>";
    new_elem += "<td class='tre-tre'>" + form.find('#id_treatment').val() + "</td>";
    new_elem += "<td class='tre-com'>" + form.find('#id_comment').val() + "</td>";
    new_elem += '<td>';
    new_elem += '<button type="button" class="btn btn-warning btn-sm edit-tre">Editar</button> ';
    new_elem += '<button type="button" class="btn btn-danger btn-sm del-tre">Eliminar</button>';
    new_elem += '</td>';
    new_elem += '</tr>';
    $('#tre-body').append(new_elem);
    $('.edit-tre').click(TreatmentEditButton);
    $('.del-tre').click(TreatmentDelButton);
    $('#modal-tre').modal('hide');
    saveEpisode();
}

function TreatmentEditSuccess(){
    var form = $('#form-tre');
    edit_treatment.find('.tre-date').html(form.find('#id_date').val());
    edit_treatment.find('.tre-tre').html(form.find('#id_treatment').val());
    edit_treatment.find('.tre-com').html(form.find('#id_comment').val());
    $('#modal-tre').modal('hide');
    saveEpisode();
}

$('#form-tre').submit(function(event){
    event.preventDefault();
    if (edit_treatment === undefined) {
        TreatmentCreateSuccess();
    } else {
        TreatmentEditSuccess();
    }
});
