var edit_record;

$( '.add-per-rec' ).click( function() {
    var elem = $( this );
    // Se limpia el formulario
    $( '#form-per-rec' ).find( 'input' ).val( '' );
    $( '#per-rec-label' ).html( 'Agregar antecedente' );
    $( '#btn-sbt-per-rec' ).html( 'Agregar' );
    $( '#modal-per-rec' ).modal( 'show' );
});

$( '.edit-per-rec' ).click( editPersonalRecordButton );

function editPersonalRecordButton() {
    var elem = $( this );
    edit_record = elem.parents( 'tr' );
    // Se limpia el formulario
    $( '#form-per-rec' ).find( 'input' ).val( '' );
    $( '#form-per-rec #id_old_category' ).val( edit_record.find( '.per-rec-cat' ).html() );
    $( '#form-per-rec #id_category' ).val( edit_record.find( '.per-rec-cat' ).html() );
    $( '#form-per-rec #id_old_record' ).val( edit_record.find( '.per-rec-rec' ).html() );
    $( '#form-per-rec #id_record' ).val( edit_record.find( '.per-rec-rec' ).html() );
    $( '#per-rec-label' ).html( 'Editar antecedente' );
    $( '#btn-sbt-per-rec' ).html( 'Editar' );
    $( '#modal-per-rec' ).modal( 'show' );
}

$( '.del-per-rec' ).click( delPersonalRecordButton );

function delPersonalRecordButton() {
    var elem = $( this );
    edit_record = elem.parents( 'tr' );
    // Se limpia el formulario
    $( '#form-per-rec #id_category' ).val( edit_record.find( '.per-rec-cat' ).html() );
    $( '#form-per-rec #id_record' ).val( edit_record.find( '.per-rec-rec' ).html() );
    var r = confirm( "¿Está seguro que desa eliminar el antecedente?" );
    if (r == true) {
        $.ajax({
            url: urlPersonalRecord,
            data: $( '#form-per-rec' ).serialize(),
            method: "DELETE",
        }).done( function() {
            edit_record.remove();
        }).fail( function() {
            alert( 'Hubo un problema con la conexión con el servidor. Por favor intente más tarde.' );
            $( '#modal-per-rec' ).modal( 'hide' );
        });
    };
}


$( document ).ready( function() {
    $( '#modal-per-rec' ).modal( { show: false } );

    // Inicializar los autocompletes
    $( '#form-per-rec #id_category' ).autocomplete({
        source: urlPersonalRecordCategoriesList,
        open: function( event, ui ) {
            $( '.ui-autocomplete' ).css( 'z-index', 2000 );
        }
    });
    $( '#form-per-rec #id_record' ).autocomplete({
        source: urlPersonalRecordRecordsList,
        open: function( event, ui ) {
            $( '.ui-autocomplete' ).css( "z-index", 2000 );
        }
    });
});

function sendPersonalRecordForm( ajaxMethod, formSuccess ) {
    $( '#form-per-rec' ).validator( 'validate' );
    if ($( '#form-per-rec .has-error' ).length > 0) {
        return false;
    };
    $.ajax({
        url: urlPersonalRecord,
        data: $( '#form-per-rec' ).serialize(),
        method: ajaxMethod,
    }).done( formSuccess ) .fail( function() {
        alert( 'Hubo un problema con la conexión con el servidor. Por favor intente más tarde.' );
        $( '#modal-per-rec' ).modal( 'hide' );
    });
};


function createPersonalRecordSuccess( data ) {
    var new_elem = '<tr>';
    new_elem += '<td class="per-rec-cat">' + data[ 'category' ] + '</td>';
    if ( data[ 'record' ] ) {
        new_elem += '<td class="per-rec-rec">' + data[ 'record' ] + '</td>';
    } else {
        new_elem += '<td class="per-rec-rec"></td>';
    }
    new_elem += '<td>';
    new_elem += '<button type="button" class="btn btn-warning btn-sm edit-per-rec">Editar</button>';
    new_elem += '<button type="button" class="btn btn-danger btn-sm del-per-rec">Eliminar</button>';
    new_elem += '</td>';
    new_elem += '</tr>';
    $( '#per-rec-body' ).append( new_elem );
    $( '.edit-per-rec' ).click( editPersonalRecordButton );
    $( '.del-per-rec' ).click( delPersonalRecordButton );
    $( '#modal-per-rec' ).modal( 'hide' );
}

function editPersonalRecordSuccess( data ) {
    edit_record.find( '.per-rec-cat' ).html( data[ 'category' ] );
    edit_record.find( '.per-rec-rec' ).html( data[ 'record' ] );
    $( '#modal-per-rec' ).modal( 'hide' );
}

$( '#form-per-rec' ).submit( function( event ) {
    event.preventDefault();
    if ($( '#form-per-rec #id_old_record' ).val() === '' ) {
        sendPersonalRecordForm( "POST", createPersonalRecordSuccess )
    } else {
        sendPersonalRecordForm( "PUT", editPersonalRecordSuccess )
    }
});

// Función para settear url de búsqueda de los records
$( '#id_category' ).blur( function() {
    var urlR = urlPersonalRecordRecordsList + '?category=' + $( '#form-per-rec #id_category' ).val();
    $( '#form-per-rec #id_record' ).autocomplete( 'option', 'source', urlR);
});
