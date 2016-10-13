var edit_diagnosis;
var csrftoken = getCookie('csrftoken');

// Configuración de las llamadas AJAX.
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        //alert('love');
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$('.add-ep-di').click(function(){
    var elem = $(this);
    // Se limpia el formulario
    $('#form-ep-di').find('input').val("");
    $('#id_date').val(moment().format('DD/MM/YYYY'))
    $('#ep-di-label').html('Agregar diagnóstico');
    $('#btn-sbt-ep-di').html('Agregar');
    $('#modal-ep-di').modal('show');
});
//clear-ep-di


$('.clear-ep-di').click(function(){
    var elem = $(this);
    // Se limpia el formulario
    $('#form-ep-di').find('input').val("");
    $('#id_date').val(moment().format('DD/MM/YYYY'))
    $('#form-ep-di').find('input').prop('readonly', false);
});


function serializeDiagnosisForm() {
    serialized_diagnosis_form = $('#form-ep-di').serializeObject()
    serialized_diagnosis_form["episode"] = id_episode_alt
    // console.log(id_episode)
    //console.log(serialized_diagnosis_form)
    if(serialized_diagnosis_form["date"]){
        serialized_diagnosis_form["date"] = moment(serialized_diagnosis_form["date"], "DD/MM/YYYY").format('YYYY-MM-DD hh:mm');
    }
    if(serialized_diagnosis_form["old_date"]){
        serialized_diagnosis_form["old_date"] = moment(serialized_diagnosis_form["old_date"], "DD/MM/YYYY").format('YYYY-MM-DD hh:mm');
    }
    return serialized_diagnosis_form
}

$('.edit-ep-di').click(DiagnosisEditButton);

function DiagnosisEditButton(){
    var elem = $(this);
    edit_diagnosis = elem.parents('tr');
    // Se limpia el formulario
    $('#form-ep-di').find('input').val("");
    $('#id_id_diag').val(edit_diagnosis.find('.ep-di-id').html());
    $('#id_date').val(edit_diagnosis.find('.ep-di-date').html());
    $('#id_old_date').val(edit_diagnosis.find('.ep-di-date').html());
    $('#id_diagnosis_category').val(edit_diagnosis.find('.ep-di-cat').html());
    $('#id_clinical_diagnosis').val(edit_diagnosis.find('.ep-di-c-d').html());
    $('#id_observations').val(edit_diagnosis.find('.ep-di-obs').html());
    $('#ep-di-label').html('Editar diagnóstico');
    $('#btn-sbt-ep-di').html('Editar');
    $('#modal-ep-di').modal('show');
}

$('.del-ep-di').click(DiagnosisDelButton);

function DiagnosisDelButton(){
    var elem = $(this);
    edit_diagnosis = elem.parents('tr');
    // Se limpia el formulario
    $('#id_id_diag').val(edit_diagnosis.find('.ep-di-id').html());
    $('#id_date').val(edit_diagnosis.find('.ep-di-date').html());
    $('#id_old_date').val(edit_diagnosis.find('.ep-di-date').html());
    $('#id_clinical_diagnosis').val(edit_diagnosis.find('.ep-di-c-d').html());
    $('#id_diagnosis_category').val(edit_diagnosis.find('.ep-di-cat').html());
    $('#id_observations').val(edit_diagnosis.find('.ep-di-obs').html());
    
    var r = confirm("¿Está seguro que desa eliminar el diagnóstico?");
    if (r == true) {
        $.ajax({
            url: urlDiagnosis,
            data: serializeDiagnosisForm(),
            method: "DELETE",
            beforeSend : function(xhr, settings){
              //call global beforeSend func
              $.ajaxSettings.beforeSend(xhr, settings);
            },
        }).done(function(){
            edit_diagnosis.remove();
            $('#form-ep-di').find('input').val("");
            $('#form-ep-di').find('input').prop('readonly', false);
        }).fail(function(){
            alert('Hubo un problema con la conexión con el servidor. Por favor intente más tarde.');
            $('#modal-ep-di').modal('hide');
        });
    };
}


$(document).ready(function(){
    $('#modal-ep-di').modal({show: false});
    // Inicializar los autocompletes urlDiagnosisCodeAutocompleteList

    $('#id_id_condition').autocomplete({
        source: urlDiagnosisCodeAutocompleteList,
        open: function(event, ui) {
            $(".ui-autocomplete").css("z-index", 2000);
        },
        select: function( event, ui ) {
            $('#id_diagnosis_category').val(ui.item.category);
            $("#id_diagnosis_category").prop('readonly', true);
            $('#id_clinical_diagnosis').val(ui.item.name);
            $("#id_clinical_diagnosis").prop('readonly', true);
            $("#id_id_condition").prop('readonly', true);
        },
    });

    $('#id_diagnosis_category').autocomplete({
        source: urlDiagnosisCategoryAutocompleteList,
        open: function(event, ui) {
            $(".ui-autocomplete").css("z-index", 2000);
        }
    });
    // Inicializar los autocompletes
     // source: function(request,response){
     //        response = urlDiagnosisAutocompleteList + "?category=" + $('#id_diagnosis_category').val();
     //    }
    $('#id_clinical_diagnosis').autocomplete({
        source:  function (request, response) {
            jQuery.get(urlDiagnosisAutocompleteList, {
                category: $('#id_diagnosis_category').val()
            }, function (data) {
                response(data);
            });
        }
    ,
        open: function(event, ui) {
            $(".ui-autocomplete").css("z-index", 2000);
        },
        select: function( event, ui ) {
    
            $("#id_diagnosis_category").prop('readonly', true);
            $('#id_id_condition').val(ui.item.code);
            $("#id_clinical_diagnosis").prop('readonly', true);
            $("#id_id_condition").prop('readonly', true);
        },
    });
});

function sendDiagnosisForm(ajaxMethod, formSuccess){
    $('#form-sub').validator('validate');
    if ($('.has-error').length > 0){
        return false;
    };
    //alert('ksks');
    $.ajax({
        url: urlDiagnosis,
        data: serializeDiagnosisForm(),
        method: ajaxMethod,
        beforeSend : function(xhr, settings){
              //call global beforeSend func
              $.ajaxSettings.beforeSend(xhr, settings);
        },
    }).done(formSuccess).fail(function(){
        alert('Hubo un problema con la conexión con el servidor. Por favor intente más tarde.');
        $('#modal-ep-di').modal('hide');
    });
};


function DiagnosisCreateSuccess(data){
    var new_elem = "<tr>";
    new_elem += "<td class='ep-di-id'>" + data["id_diag"] + "</td>";
    new_elem += "<td class='ep-di-date' data-date='" + data["date"] + "''>" + moment(data["date"], 'YYYY-MM-DD hh:mm').format("DD/MM/YYYY") + "</td>";
    new_elem += "<td class='ep-di-cat'>" + data["diagnosis_category"] + "</td>";
    new_elem += "<td class='ep-di-c-d'>" + data["clinical_diagnosis"] + "</td>";
    new_elem += "<td class='ep-di-obs'>" + data["observations"] + "</td>";
    new_elem += '<td>';
    new_elem += '<button type="button" class="btn btn-warning btn-sm edit-ep-di">Editar</button>';
    new_elem += '<button type="button" class="btn btn-danger btn-sm del-ep-di">Eliminar</button>';
    new_elem += '</td>';
    new_elem += '</tr>';
    $('#ep-di-body').append(new_elem);
    $('.edit-ep-di').click(DiagnosisEditButton);
    $('.del-ep-di').click(DiagnosisDelButton);
    $('#modal-ep-di').modal('hide');
    $('#form-ep-di').find('input').val("");
    $('#form-ep-di').find('input').prop('readonly', false);
}
//moment(data["date"], 'YYYY-MM-DD hh:mm').format("DD/MM/YYYY") 
function DiagnosisEditSuccess(data){
    edit_diagnosis.find('.ep-di-date').html(moment(data["date"], 'YYYY-MM-DD hh:mm').format("DD/MM/YYYY"));
    edit_diagnosis.find('.ep-di-cat').html(data["diagnosis_category"]);
    edit_diagnosis.find('.ep-di-c-d').html(data["clinical_diagnosis"]);
    edit_diagnosis.find('.ep-di-obs').html(data["observations"]);
    $('#modal-ep-di').modal('hide');
}

$('#form-ep-di').submit(function(event){
    event.preventDefault();
    DiagnosisSubmitForm();
});

//Función para settear url de búsqueda de los diagnósticos
$('#id_diagnosis_category').blur(function(){
    var urlRD = urlDiagnosisCategoryAutocompleteList + '?category=' + $('#id_diagnosis_category').val();
    $("#id_diagnosis").autocomplete("option", "source", urlRD);
});

function DiagnosisSubmitForm(){
    if ($('#id_old_date').val() === "") {
        sendDiagnosisForm("POST", DiagnosisCreateSuccess)
    } else {
        sendDiagnosisForm("PUT", DiagnosisEditSuccess)
    }
};

