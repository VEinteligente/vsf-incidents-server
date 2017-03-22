var edit_development;

$('.add-dev').click(function(){
    edit_development = undefined;
    var elem = $(this);
    var form = $('#form-dev');
    // Se limpia el formulario
    form.find('input').val("");
    form.find('#id_date').val(moment().format('DD/MM/YYYY'))
    $('#dev-label').html('Agregar evolución');
    $('#btn-sbt-dev').html('Agregar');
    $('#modal-dev').modal('show');
});


function serializeDevelopments() {
    var devs = [];
    $('.development').each(function(){
        var dev = {};
        dev["date"] = moment($(this).find('.dev-dte').html(), "DD/MM/YYYY").format('YYYY-MM-DD hh:mm');
        dev["weight"] = $(this).find('.dev-wei').html();
        dev["height"] = $(this).find('.dev-hei').html();
        dev["pulse"] = $(this).find('.dev-pul').html();
        dev["systolic_blood_pressure"] = $(this).find('.dev-pas').html();
        dev["diastolic_blood_pressure"] = $(this).find('.dev-pad').html();
        dev["temperature"] = $(this).find('.dev-tem').html();
        dev["respiratory_rate"] = $(this).find('.dev-res').html();
        dev["observations"] = $(this).find('.dev-obs').html();
        devs.push(dev);
    });
    return devs;
}

$(document).on('click', '.edit-dev', DevelopmentEditButton);

function DevelopmentEditButton(){
    var elem = $(this);
    edit_development = elem.parents('.tab-dev');
    // Se limpia el formulario
    var form = $('#form-dev');
    form.find('#id_date').val(edit_development.find('.dev-dte').html());
    form.find('#id_weight').val(edit_development.find('.dev-wei').html());
    form.find('#id_height').val(edit_development.find('.dev-hei').html());
    form.find('#id_pulse').val(edit_development.find('.dev-pul').html());
    form.find('#id_systolic_blood_pressure').val(edit_development.find('.dev-pas').html());
    form.find('#id_diastolic_blood_pressure').val(edit_development.find('.dev-pad').html());
    form.find('#id_temperature').val(edit_development.find('.dev-tem').html());
    form.find('#id_respiratory_rate').val(edit_development.find('.dev-res').html());
    form.find('#id_observations').val(edit_development.find('.dev-obs').html());
    $('#dev-label').html('Editar evolución');
    $('#btn-sbt-dev').html('Editar');
    $('#modal-dev').modal('show');
}

$(document).on('click', '.del-tre', DevelopmentDelButton);

function DevelopmentDelButton(){
    var elem = $(this);
    edit_treatment = elem.parents('.tab-dev');
    
    var r = confirm("¿Está seguro que desa eliminar el tratamiento?");
    if (r == true) {
        edit_treatment.remove();
        saveEpisode();
    };
}

$(document).ready(function(){
    $('#modal-dev').modal({show: false});
    $('#form-dev').find('#id_date').inputmask("dd/mm/yyyy", {"placeholder": "dd/mm/yyyy"});
    $('#form-dev').find('#id_date').datepicker({
        autoclose: true,
        format: 'dd/mm/yyyy',
        endDate: '0d',
        language: 'es-ES',
        todayBtn: true
    });
});

function DevelopmentCreateSuccess(){
    var form = $('#form-dev');
    var devsCount = $('#devs-tabs li').length + 1;
    var weight = form.find('#id_weight').val();
    var height = form.find('#id_height').val();
    var pas = form.find('#id_systolic_blood_pressure').val();
    var pad = form.find('#id_diastolic_blood_pressure').val();
    // Se desactiva el tab activo
    $('#devs-tabs .active').find('[aria-expanded="true"]').attr('aria-expanded', 'false');
    $('#devs-tabs .active').removeClass('active');
    $('#devs-content .active').removeClass('active');

    var new_li = '<li class="active">';
    new_li += '<a aria-expanded="true" href="#dev_tab_' + devsCount + '" data-toggle="tab">' + form.find('#id_date').val() + '</a>';
    new_li += '</li>';
    new_li = $(new_li);

    var new_table = '<div id="dev_tab_' + devsCount + '" class="tab-pane tab-dev active">';
    new_table += '<table class="development table table-striped">';
    new_table += '<tr><td><strong>Peso</strong></td><td><strong>Talla</strong></td><td><strong>Superficie Corporal</strong></td><td><strong>I.M.C.</strong></td><td><strong>Temperatura ºC</strong></td></tr>';
    new_table += '<tr>';
    new_table += "<td class='dev-wei'>" + weight + "</td>";
    new_table += "<td class='dev-hei'>" + height + "</td>";
    new_table += "<td class='dev-cor'>" + calBoodySurface(weight, height) + "</td>";
    new_table += "<td class='dev-imc'>" + calIMC(weight, height) + "</td>";
    new_table += "<td class='dev-tem'>" + form.find('#id_temperature').val() + "</td>";
    new_table += '</tr>';
    new_table += '<tr><td><strong>Pulso</strong></td><td><strong>Presión arterial sistólica</strong></td><td><strong>Presión arterial diastólica</strong></td><td><strong>Presión arterial media</strong></td><td><strong>Frec. Respiratoria</strong></td></tr>';
    new_table += '<tr>';
    new_table += "<td class='dev-pul'>" + form.find('#id_pulse').val() + "</td>";
    new_table += "<td class='dev-pas'>" + pas + "</td>";
    new_table += "<td class='dev-pad'>" + pad + "</td>";
    new_table += "<td class='dev-pam'>" + calPM(pas, pad) + "</td>";
    new_table += "<td class='dev-res'>" + form.find('#id_respiratory_rate').val() + "</td>";
    new_table += '</tr>';
    new_table += '<tr><td colspan="5"><strong>Observaciones</strong></td></tr>';
    new_table += '<tr>';
    new_table += '<td class="dev-obs" colspan="5">' + form.find('#id_observations').val() + '</td>';
    new_table += '</tr>';
    new_table += '<tr style="display: none;"><td class="dev-dte">' + form.find('#id_date').val() + '</td></tr>';
    new_table += '</table>';
    new_table += '<button type="button" class="btn btn-warning btn-sm edit-dev">Editar</button> ';
    new_table += '<button type="button" class="btn btn-danger btn-sm del-dev">Eliminar</button>';
    new_table = $(new_table)
    $('#devs-content').append(new_table);
    $('#li-add-dev').before(new_li);
    $('#modal-dev').modal('hide');
    saveEpisode();
}

function DevelopmentEditSuccess(){
    var form = $('#form-dev');
    var weight = form.find('#id_weight').val();
    var height = form.find('#id_height').val();
    var pas = form.find('#id_systolic_blood_pressure').val();
    var pad = form.find('#id_diastolic_blood_pressure').val();
    edit_development.find('.dev-date').html(form.find('#id_date').val());
    edit_development.find('.dev-wei').html(weight);
    edit_development.find('.dev-hei').html(height);
    edit_development.find('.dev-cor').html(calBoodySurface(weight, height));
    edit_development.find('.dev-imc').html(calIMC(weight, height));
    edit_development.find('.dev-pul').html(form.find('#id_pulse').val());
    edit_development.find('.dev-pas').html(pas);
    edit_development.find('.dev-pad').html(pad);
    edit_development.find('.dev-pam').html(calPM(pas, pad));
    edit_development.find('.dev-tem').html(form.find('#id_temperature').val());
    edit_development.find('.dev-res').html(form.find('#id_respiratory_rate').val());
    edit_development.find('.dev-obs').html(form.find('#id_observations').val());
    $('#modal-dev').modal('hide');
    saveEpisode();
}

$('#form-dev').submit(function(event){
    event.preventDefault();
    $('#form-dev').validator('validate');
    if ($('#form-dev').find('.has-error').length > 0){
        return false;
    };
    if (edit_development === undefined) {
        DevelopmentCreateSuccess();
    } else {
        DevelopmentEditSuccess();
    }
});
