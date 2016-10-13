var $edit_spex = undefined;

$( document ).on( 'click', '.add-spex', SPExAddButton );
$( document ).on( 'click', '.edit-spex', SPExEditButton );
$( document ).on( 'click', '.del-spex', SPExDelButton );

function serializeSPExs() {
    var spexs = [];
    $( '.spex' ).each(function(){
        var $elem = $( this );
        var spex = {};
        spex[ 'date' ] =  moment( $elem.find( '.spex-date' ).html(), 'DD/MM/YYYY' ).format( 'YYYY-MM-DD hh:mm' );
        spex[ 'region' ] = $elem.find( '.spex-region' ).html();
        spex[ 'comment' ] = $elem.find( '.spex-com' ).html();
        spexs.push( spex );
    });
    return spexs;
}

function SPExAddButton() {
    $edit_spex = undefined;
    var elem = $( this );
    var form = $( '#form-spex' );
    // Se limpia el formulario
    form.find( 'input' ).val( '' );
    form.find( 'textarea' ).val( '' );
    form.find( '#id_date' ).val( moment().format( 'DD/MM/YYYY' ) );
    $( '#spex-label' ).html( 'Agregar examen físico específico' );
    $( '#btn-sbt-spex' ).html( 'Agregar' );
    $( '#modal-spex' ).modal( 'show' );
}

function SPExEditButton(){
    var $elem = $( this );
    var form = $( '#form-spex' );

    // Elemento a editar
    $edit_spex = $elem.parents( 'tr' );

    // Se limpia el formulario
    form.find( 'input' ).val( '' );
    form.find( 'textarea' ).val( '' );

    // Se agregan los datos correspondientes
    form.find( '#id_date' ).val( $edit_spex.find( '.spex-date' ).html() );
    form.find( '#id_region' ).val( $edit_spex.find( '.spex-region' ).html() );
    form.find( '#id_comment' ).val( $edit_spex.find( '.spex-com' ).html() );

    // Se actualiza el URL para la búsqueda de hallazgos
    updateAutocompleteSPExsURL();

    $( '#spex-label' ).html( 'Editar examen físico específico' );
    $( '#btn-sbt-spex' ).html( 'Editar' );
    $( '#modal-spex' ).modal( 'show' );
}

function SPExDelButton(){
    var $elem = $( this );
    $edit_spex = $elem.parents( 'tr' );

    var r = confirm( '¿Está seguro que desa eliminar el examen físico específico?' );
    if ( r == true ) {
        $edit_spex.remove();
        saveEpisode();
    };
}

function updateAutocompleteSPExsURL() {
    var urlR = urlSPExsList + '?region=' + $( '#form-spex #id_region' ).val();
    alert(urlR);
    $( '#form-spex #id_autocomplete' ).autocomplete( 'option', 'source', urlR );
}

$( document ).ready( function() {
    $( '#modal-spex' ).modal( { show: false } );
    $( '#form-spex #id_region' ).autocomplete({
        source: urlBodyRegionsList,
        open: function( event, ui ) {
            $( '.ui-autocomplete' ).css( 'z-index', 2000 );
        }
    });

    $( '#form-spex #id_autocomplete' ).autocomplete({
        source: urlSPExsList,
        open: function( event, ui ) {
            $( '.ui-autocomplete' ).css( 'z-index', 2000 );
        },
        select: function( event, ui ) {
            var $target = $( '#form-spex #id_comment' );
            var actual = $target.val();
            var newValue = ui.item.value;

            if ( actual.includes( newValue ) ) {
                alert( 'La observación seleccionada ya ha sido incluida.' );
                return false;
            }

            if ( actual == '' ) {
                $target.val( newValue );
            }
            else {
                $target.val( actual + ', ' + newValue );
            }

            $( '#form-spex #id_autocomplete' ).val( '' );

            return false;
        }
    });

    // Función para settear url de búsqueda de los records
    $( '#form-spex #id_region' ).change( updateAutocompleteSPExsURL() );
});

function SPExCreateSuccess(){
    var $form = $( '#form-spex' );
    var new_elem = '<tr class="spex">';
    new_elem += '<td class="spex-date">' + $form.find( '#id_date' ).val() + '</td>';
    new_elem += '<td class="spex-region">' + $form.find( '#id_region' ).val() + '</td>';
    new_elem += '<td class="spex-com">' + $form.find( '#id_comment' ).val() + '</td>';
    new_elem += '<td>';
    new_elem += '<button type="button" class="btn btn-warning btn-sm edit-spex">Editar</button> ';
    new_elem += '<button type="button" class="btn btn-danger btn-sm del-spex">Eliminar</button>';
    new_elem += '</td>';
    new_elem += '</tr>';
    $( '#spex-body' ).append( new_elem );
    $( '#modal-spex' ).modal( 'hide' );
    saveEpisode();
}

function SPExEditSuccess(){
    var $form = $( '#form-spex' );
    $edit_spex.find( '.spex-date' ).html( $form.find( '#id_date' ).val() );
    $edit_spex.find( '.spex-region' ).html( $form.find( '#id_region' ).val() );
    $edit_spex.find( '.spex-com' ).html( $form.find( '#id_comment' ).val() );
    $( '#modal-spex' ).modal( 'hide' );
    saveEpisode();
}

$( '#form-spex' ).submit( function( event ) {
    event.preventDefault();
    if ($edit_spex === undefined) {
        SPExCreateSuccess();
    } else {
        SPExEditSuccess();
    }
});
