$(function () {
	$('#start_date_picker').datetimepicker({format: 'YYYY-MM-DD'});
});
$(function () {
	$('#end_date_picker').datetimepicker({format: 'YYYY-MM-DD'});
});

var repeatCheck = document.getElementById("repeatCheck");
var rruleContainer = document.getElementById("rruleContainer");
var rruleField = document.getElementById("id_rrule");
repeatCheck.addEventListener("change", toggleRruleContainer);
document.getElementById("form").addEventListener("submit", formSubmit);

var rrule_str = "";

toggleRruleContainer();
function toggleRruleContainer(){
	if (repeatCheck.checked){
		rruleContainer.style.display = "block";
	}
	else {
		rruleContainer.style.display = "none";
	}
}

function createRuleStr(){
	return rrule_str;
}

function formSubmit(){
	if (repeatCheck.checked){
		rruleField.value = createRuleStr();
	}
}