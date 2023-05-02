$(document).ready(function () {
    $("body").attr({
        "data-spy": "scroll",
        "data-target": ".navbar"
    }).scrollspy({
        offset: 150
    });

    // Disable specialization checkboxes when number of doctors is 0
    $("#inputDoctors").change(function () {
        if ($(this).val() == 0) {
            $('#specialization_fieldset').find('input').prop('checked','');
            $("#specialization_fieldset").prop("disabled", true);
            $("#specialization_fieldset").prop("required", false);
        }
        else {
            $("#specialization_fieldset").prop("disabled", false);
            $("#specialization_fieldset").prop("required", true);
        }
    });

    // Disable/enable select option for cigarettes frequency
    $("#inputCigarettes").change(function () {
        if ($(this).val() == "tak") {
            $("#cigarettes_freq").prop("disabled", false);
            $("#cigarettes_freq").prop("required", true);
        }
        else {
            $("#cigarettes_freq")[0].selectedIndex = 0;
            $("#cigarettes_freq").prop("disabled", true);
            $("#cigarettes_freq").prop("required", false);
        }
    });

    // Disable/enable select option for alcohol frequency
    $("#inputAlcohol").change(function () {
        if ($(this).val() == "tak") {
            $("#alcohol_freq").prop("disabled", false);
            $("#alcohol_freq").prop("required", true);
        }
        else {
            $("#alcohol_freq")[0].selectedIndex = 0;
            $("#alcohol_freq").prop("disabled", true);
            $("#alcohol_freq").prop("required", false);
        }
    });

    $("#addMedicine button").click(function () {
        AddButtonFunc();
    });

    // Confirm deletion of a medicine
    $("main").on("click", ".deleteMedicine", function () {
        let text = "Czy chcesz usunąć lek?";
        if (confirm(text) == true) {
            number -= 1;
            let value = "#" + $(this).val();
            $( value ).remove();
        }
    });
    // Example starter JavaScript for disabling form submissions if there are invalid fields

    'use strict';

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation');

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
      .forEach(function (form) {
        form.addEventListener('submit', function (event) {
          if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
          }

          if (confirm("Zatwierdź formularz") == false) {
            event.preventDefault();
          }


          form.classList.add('was-validated')
        }, false);
      })

});

var number = 1;
function AddButtonFunc() {
    number += 1;

    // Copy first medicine's fields and change its id
    let medicine = $( "#medicine1" ).clone().attr("id", "medicine"+number);

    // Create delete button
    let delete_button = '<button class="deleteMedicine btn btn-danger w-100 mt-2" type="button" value="medicine' +number+'">Usuń</button>';

    // Insert delete button into compliance div
    $(".medCompliance", medicine).append(delete_button);

    // Clear input fields
    $("input", medicine).val("");

    $("h5", medicine).text("Lek " + number + ":");

    // Insert fields for new medicine before "add another medicine" button
    $( "#addMedicine" ).before(medicine);
}