var digitalRadIndex = 1;
var fysiskRadIndex = 1;

$(document).ready(() => {
    $('#digitalRader').val(digitalRadIndex);
    $('#fysiskRader').val(fysiskRadIndex)
});

function nyDigitalRad() {
    $(document).ready(() => {
        digitalRadIndex++;
        $('#digitalRader').val(digitalRadIndex);
        let rad = '<div class="form-row"><div class="form-group col-3"><label for="kilde">Kilde</label><input type="text" class="form-control" id="kilde" name="kilde'+ digitalRadIndex +'" required></div><div class="form-group col-2"><label for="DLutgivelse">DL utgivelse</label><input type="number" class="form-control" id="DLutgivelse" name="DLutgivelse'+ digitalRadIndex +'" min="0"></div><div class="form-group col-2"><label for="DLspor">DL spor</label><input type="number" class="form-control" id="DLspor" name="DLspor'+ digitalRadIndex +'" min="0"></div><div class="form-group col-2"><label for="streams">Streams</label><input type="number" class="form-control" id="streams" name="streams'+ digitalRadIndex +'" min="0"></div><div class="form-group col-2"><label for="brutto">Brutto</label><input type="number" class="form-control" id="brutto" name="brutto'+ digitalRadIndex +'" min="0" step="any" required></div></div>';
        $("#nyDigitalRad").append(rad);
    });
}

function nyFysiskRad() {
    $(document).ready(() => {
        fysiskRadIndex++;
        $('#fysiskRader').val(fysiskRadIndex);
        let rad = '<div class="form-row"><div class="form-group col-3"><label for="kilde">Kilde</label><input type="text" class="form-control" id="kilde" name="kilde'+ fysiskRadIndex +'" required></div><div class="form-group col-2"><label for="antall">Antall</label><input type="number" class="form-control" id="antall" name="antall'+ fysiskRadIndex +'" min="0"></div><div class="form-group col-2"><label for="inntekter">Inntekter</label><input type="number" class="form-control" id="inntekter" name="inntekter'+ fysiskRadIndex +'" min="0"></div><div class="form-group col-2"><label for="kostnader">Kostnader</label><input type="number" class="form-control" id="kostnader" name="kostnader'+ fysiskRadIndex +'" min="0"></div><div class="form-group col-2"><label for="brutto">Brutto</label><input type="number" class="form-control" id="brutto" name="brutto'+ fysiskRadIndex +'" min="0" step="any" required></div></div>';
        $("#nyFysiskRad").append(rad);
    });
}