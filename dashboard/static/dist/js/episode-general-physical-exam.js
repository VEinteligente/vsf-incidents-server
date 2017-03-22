$('#form-gen-phy-ex #id_weight').keyup(calBodySurfaceGPEX);
$('#form-gen-phy-ex #id_height').keyup(calBodySurfaceGPEX);

function calBodySurfaceGPEX() {
    var weight = parseInt($('#id_weight').val());
    var height = parseInt($('#id_height').val());
    if ((weight > 0) && (height > 0)) {
        $('#id_body_surface').val(calBoodySurface(weight, height));
        //Cálculo del IMC
        $('#id_imc').val(calIMC(weight, height));
    }
}


// Función para calcular la superficie corporal
function calBoodySurface(weight, height) {
    if ((weight > 0) && (height > 0)) {
        var calc;
        // Cálculo de la superficie corporal media
        calc = (Math.pow(weight, 0.425) * Math.pow(height, 0.725));
        calc = 0.007184 * calc;
        return (Math.round(calc * 100) / 100);
    }
    return 0;
}

// Función para calcular el IMC
function calIMC(weight, height) {
    if ((weight > 0) && (height > 0)) {
        var calc;
        calc = weight / Math.pow((height / 100), 2);
        return (Math.round(calc * 100) / 100);
    }
    return 0;
}

function calPM(pas, pad) {
    if ((pas > 0) && (pad > 0)) {
        var calc;
        // Cálculo de la presión arterial media
        calc = pad + ((pas - pad) / 3);
        return calc;
    }
    return 0;
}


$('#form-gen-phy-ex #id_systolic_blood_pressure').keyup(calBloodPressureGPEX);
$('#form-gen-phy-ex #id_diastolic_blood_pressure').keyup(calBloodPressureGPEX);

function calBloodPressureGPEX() {
    var pas = parseInt($('#id_systolic_blood_pressure').val());
    var pad = parseInt($('#id_diastolic_blood_pressure').val());
    if ((pas > 0) && (pad > 0)) {
        $('#id_median_blood_presure').val(calPM(pas, pad));
        //Cálculo del IMC
        if ((pas < 120) && (pad < 80)) {
            $('#id_jnc').val("Óptima");
        } else if ((pas >= 120) && (pas < 130) && (pad < 85)){
            $('#id_jnc').val("Normal");
        } else if ((pas >= 130) && (pas < 140) && (pad >= 85) && (pad < 90)){
            $('#id_jnc').val("Límite superior");
        } else if (((pas >= 140) && (pas < 160)) || ((pad >= 90) && (pad < 100))){
            $('#id_jnc').val("Hipertensión arterial grado I");
        } else if (((pas >= 160) && (pas < 180)) || ((pad >= 100) && (pad < 110))){
            $('#id_jnc').val("Hipertensión arterial grado II");
        } else if ((pas >= 180) || (pad >= 110)){
            $('#id_jnc').val("Hipertensión arterial grado III");
        } else {
            $('#id_jnc').val("N/D");
        }
    }
}

function serializeGralPhysicalExam() {
    var $form = $( '#form-gen-phy-ex' );
    var gralPhysicalEx = $form.serializeObject();

    gralPhysicalEx[ 'date' ] = moment( $form.find( '#id_date' ).val(), 'DD/MM/YYYY' ).format( 'YYYY-MM-DD hh:mm' );

    return gralPhysicalEx;
}
