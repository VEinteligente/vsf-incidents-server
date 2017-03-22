var $edit_func_ex = undefined;

$( document ).on( 'click', '.add-func-ex', FuncExAddButton );
$( document ).on( 'click', '.edit-func-ex', FuncExEditButton );
$( document ).on( 'click', '.del-func-ex', FuncExDelButton );

function serializeFuncExs() {
    var func_exs = [];
    $( '.func-ex' ).each( function() {
        var $elem = $( this );
        var func_ex = {};
        func_ex[ 'date' ] =  moment( $elem.find( '.func-ex-date' ).html(), 'DD/MM/YYYY' ).format( 'YYYY-MM-DD hh:mm' );
        func_ex[ 'system' ] = $elem.find( '.func-ex-system' ).html();
        func_ex[ 'findings' ] = $elem.find( '.func-ex-findings' ).html();
        func_exs.push( func_ex );
    });
    return func_exs;
}

function FuncExAddButton() {
    $edit_func_ex = undefined;
    var elem = $( this );
    var form = $( '#form-func-ex' );
    // Se limpia el formulario
    form.find( 'input' ).val( '' );
    form.find( 'textarea' ).val( '' );
    form.find( '#id_date' ).val( moment().format( 'DD/MM/YYYY' ) );
    $( '#func-ex-label' ).html( 'Agregar examen funcional' );
    $( '#btn-sbt-func-ex' ).html( 'Agregar' );
    $( '#modal-func-ex' ).modal( 'show' );
}

function FuncExEditButton(){
    var $elem = $( this );
    var form = $( '#form-func-ex' );

    // Elemento a editar
    $edit_func_ex = $elem.parents( 'tr' );

    // Se limpia el formulario
    form.find( 'input' ).val( '' );
    form.find( 'textarea' ).val( '' );

    // Se agregan los datos correspondientes
    form.find( '#id_date' ).val( $edit_func_ex.find( '.func-ex-date' ).html() );
    form.find( '#id_system' ).val( $edit_func_ex.find( '.func-ex-system' ).html() );
    form.find( '#id_findings' ).val( $edit_func_ex.find( '.func-ex-findings' ).html() );

    // Se actualiza el URL para la búsqueda de hallazgos
    updateAutocompleteFuncExURL();

    $( '#func-ex-label' ).html( 'Editar examen funcional' );
    $( '#btn-sbt-func-ex' ).html( 'Editar' );
    $( '#modal-func-ex' ).modal( 'show' );
}

function FuncExDelButton(){
    var $elem = $( this );
    $edit_func_ex = $elem.parents( 'tr' );

    var r = confirm( '¿Está seguro que desa eliminar el examen funcional?' );
    if ( r == true ) {
        $edit_func_ex.remove();
        saveEpisode();
    };
}

function updateAutocompleteFuncExURL() {
    var urlR = urlFuncExsFindingsList + '?category=' + $( '#form-func-ex #id_system' ).val();
    $( '#form-func-ex #id_autocomplete' ).autocomplete( 'option', 'source', urlR );
}


$( document ).ready( function() {
    $( '#modal-func-ex' ).modal( { show: false } );

    $( '#form-func-ex #id_system' ).autocomplete({
        source: urlFuncExsSystemsList,
        open: function( event, ui ) {
            $( '.ui-autocomplete' ).css( 'z-index', 2000 );
        }
    });

    $( '#form-func-ex #id_autocomplete' ).autocomplete({
        source: urlFuncExsFindingsList,
        open: function( event, ui ) {
            $( '.ui-autocomplete' ).css( 'z-index', 2000 );
        },
        select: function( event, ui ) {
            var $target = $( '#form-func-ex #id_findings' );
            var actual = $target.val();
            var newValue = ui.item.value;

            if ( actual.includes( newValue ) ) {
                alert( 'El hallazgo seleccionado ya ha sido incluido.' );
                return false;
            }

            if ( actual == '' ) {
                $target.val( newValue );
            }
            else {
                $target.val( actual + ', ' + newValue );
            }

            $( '#form-func-ex #id_autocomplete' ).val( '' );

            return false;
        }
    });

    // Función para settear url de búsqueda de los hallazgos
    $( '#form-func-ex #id_system' ).blur( updateAutocompleteFuncExURL() );
});



function FuncExCreateSuccess(){
    var $form = $( '#form-func-ex' );
    var new_elem = '<tr class="func-ex">';
    new_elem += '<td class="func-ex-date">' + $form.find( '#id_date' ).val() + '</td>';
    new_elem += '<td class="func-ex-system">' + $form.find( '#id_system' ).val() + '</td>';
    new_elem += '<td class="func-ex-findings">' + $form.find( '#id_findings' ).val() + '</td>';
    new_elem += '<td>';
    new_elem += '<button type="button" class="btn btn-warning btn-sm edit-func-ex">Editar</button> ';
    new_elem += '<button type="button" class="btn btn-danger btn-sm del-func-ex">Eliminar</button>';
    new_elem += '</td>';
    new_elem += '</tr>';
    $( '#func-ex-body' ).append( new_elem );
    $( '#modal-func-ex' ).modal( 'hide' );
    saveEpisode();
}

function FuncExEditSuccess(){
    var $form = $( '#form-func-ex' );
    $edit_func_ex.find( '.func-ex-date' ).html( $form.find( '#id_date' ).val() );
    $edit_func_ex.find( '.func-ex-system' ).html( $form.find( '#id_system' ).val() );
    $edit_func_ex.find( '.func-ex-findings' ).html( $form.find( '#id_findings' ).val() );
    $( '#modal-func-ex' ).modal( 'hide' );
    saveEpisode();
}

$( '#form-func-ex' ).submit( function( event ) {
    event.preventDefault();
    if ( $edit_func_ex === undefined ) {
        FuncExCreateSuccess();
    } else {
        FuncExEditSuccess();
    }
});
