var radIndex = 1;

$(document).ready(() => {$('#rader').val(radIndex);});

function nyDigitalRad() {
    $(document).ready(() => {
        radIndex++;
        $('#rader').val(radIndex);
        let rad = '<div class="form-row"><div class="form-group col-3"><label for="kilde">Kilde</label><input type="text" class="form-control id="kilde'+ radIndex +'" name="kilde" required></div><div class="form-group col-3"><label for="DLutgivelse">DL utgivelse</label><input type="number" class="form-control id="DLutgivelse'+ radIndex +'" name="DLutgivelse" min="0"></div><div class="form-group col-3"><label for="DLspor">DL spor</label><input type="number" class="form-control id="DLspor'+ radIndex +'" name="DLspor" min="0"></div><div class="form-group col-3"><label for="streams">Streams</label><input type="number" class="form-control id="streams'+ radIndex +'" name="streams" min="0"></div></div>';
        $("#nyDigitalRad").append(rad);
    });
}