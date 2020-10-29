import { RRule, RRuleSet, rrulestr } from '/static/cal/rrule.js';

$(function () {
	$('#start_date_picker').datetimepicker({format: 'YYYY-MM-DD'});
});
$(function () {
	$('#end_date_picker').datetimepicker({format: 'YYYY-MM-DD'});
});

$(".weekByDay").get(moment($('#id_start_date').val()).day()).checked = true; //select relevant week day
document.getElementById('monthByDay').options[moment($('#id_start_date').val()).day()].selected = 'selected'; //select relevant week day

$("input:checkbox.buttonCheckbox:checked").parent().addClass("active");
$(document).on("click", "input:checkbox.buttonCheckbox" , function() {
	$(this).parent().toggleClass("active");
});

var repeatCheck = document.getElementById("repeatCheck");
var rruleContainer = document.getElementById("rruleContainer");
var rruleField = document.getElementById("id_rrule");

repeatCheck.addEventListener("change", toggleRruleContainer);
document.getElementById("form").addEventListener("submit", formSubmit);
$('input:radio[name=freq]').change(freqIntervalChange);
$('#interval').change(freqIntervalChange);
$('input:radio[name=monthSelect]').change(monthShowHide);

var rruleFreq = "";
var rruleInterval = "";
var rruleByDay = "";
var rruleByMonth = "";
var rruleByMonthDay = "";
var rruleBySetPos = "";

toggleRruleContainer();
function toggleRruleContainer(){
	if (repeatCheck.checked){
		rruleContainer.style.display = "block";
	}
	else {
		rruleContainer.style.display = "none";
	}
}

function clearRruleVars(){
	rruleByDay = rruleByMonth = rruleByMonthDay = rruleBySetPos = "";
}

function createRruleStr(){
	var rrule_str = "DTSTART:" + $('#id_start_date').val().replace(/-/g, '');
	if($('#id_start_time').val()){rrule_str += "T" + $('#id_start_time').val().replace(/:/g, "") + "00";}
	else{rrule_str += "T000000";}
	rrule_str += "\nRRULE:";
	if (rruleFreq){rrule_str += "FREQ:" + rruleFreq + ";";}
	if (rruleInterval != 1){rrule_str += "INTERVAL:" + rruleInterval + ";";}
	if (rruleByDay){rrule_str += "BYDAY:" + rruleByDay + ";";}
	if (rruleByMonth){rrule_str += "BYMONTH:" + rruleByMonth + ";";}
	if (rruleByMonthDay){rrule_str += "BYMONTHDAY:" + rruleByMonthDay + ";";}
	if (rruleBySetPos){rrule_str += "BYSETPOS:" + rruleBySetPos + ";";}

	if (rrule_str.slice("-1") === ";"){rrule_str = rrule_str.substring(0, rrule_str.length-1);} //remove trailing semicolons
	return rrule_str;
}

function formSubmit(){
	if (repeatCheck.checked){
		rruleField.value = createRruleStr();
	}
}

$("input").click(function(){
	console.log(createRruleStr());
});


freqIntervalChange();

function freqIntervalChange(){
	rruleFreq = $('input:radio[name=freq]:checked').val();
	rruleInterval = $('#interval').val();

	var freqName = $('input:radio[name=freq]:checked').data("name");

	if ($('#interval').val() > 1){
		$('#freqDisplay').text(freqName + "s");
	} else{ $('#freqDisplay').text(freqName);}
	//^set the display to the frequency name plus or minus an 's' for plurality

	$('.freqContainer').css("display", "none");
	if (['week', 'month', 'year'].includes(freqName)){
		$('#' + freqName + "Container").css("display", "block");
	}
	//show the relevant container depending on the frequency, if applicable
	if (freqName == "day"){clearRruleVars();}
	else if (freqName == "week"){clearRruleVars(); weekByDay();}
	else if (freqName == "month"){clearRruleVars(); monthShowHide(); monthByMonthDay(); monthByDay();}
	else if (freqName == "year"){clearRruleVars();}
}

$(".weekByDay").click(weekByDay);
function weekByDay(){
	rruleByDay = "";
	$('.weekByDay:checked').each(function() {
		rruleByDay += $(this).attr('id') + ",";
	});
	if (rruleByDay.slice("-1") === ","){rruleByDay = rruleByDay.substring(0, rruleByDay.length-1);} //remove any trailing commas, if necessary
}

monthShowHide();
function monthShowHide(){
	clearRruleVars();
	var selectedValue = $('input:radio[name=monthSelect]:checked').val();
	if (selectedValue == "bymonthday"){
		$('.monthByDays').css("display", "none");
		$('.monthByMonthDays').css("display", "block");
	}
	else if (selectedValue == "byday"){
		$('.monthByMonthDays').css("display", "none");
		$('.monthByDays').css("display", "block");
	}
}
//^show/hide relevant month section thing

$(document).on("click", ".monthByMonthDay" , function() {monthByMonthDay();});
function monthByMonthDay(){
	rruleByDay=""; //this value should not be set if the user is somehow here
	rruleByMonthDay = "";
	$('.monthByMonthDay:checked').each(function() {
		rruleByMonthDay += $(this).attr('id') + ",";
	});
	if (rruleByDay.slice("-1") === ","){rruleByDay = rruleByDay.substring(0, rruleByDay.length-1);} //remove any trailing commas, if necessary
}

createMonthElements();
var month = $('#id_start_date').val().substring(5,7);
$('#id_start_date').change(function() {
	$(".weekByDay").get(moment($('#id_start_date').val()).day()).checked = true; //select relevant week day
	document.getElementById('monthByDay').options[moment($('#id_start_date').val()).day()].selected = 'selected'; //select relevant week day
	var newMonth = $(this).val().substring(5,7);
	if (newMonth != month){
		createMonthElements();
		month = newMonth;
	}
});
function createMonthElements(){
	$('.monthByMonthDays').empty();
	var daysInMonth = moment($('#id_start_date').val()).daysInMonth();
	var generatedElements = "";
	for(var i=1; i<= daysInMonth; i++){
		generatedElements += '<label for="' + i + '" class="buttonCheckbox"><input type="checkbox" id="' + i + '" class="buttonCheckbox monthByMonthDay">' + i + '</label>';
	}
	$('.monthByMonthDays').append(generatedElements);
}
//^when the date changes, update the month options so that it goes up to 30, or 31, or whatever


$("#monthByDay").change(monthByDay);
$("#monthBySetPos").change(monthByDay);
function monthByDay(){
	rruleByMonthDay = ""; //this value should not be set if the user is somehow here
	rruleBySetPos = $('#monthBySetPos').val();
	rruleByDay = $('#monthByDay').val();
}

$(document).on("change", "input:radio[name=freq] #interval input:checkbox.buttonCheckbox #monthByDay #monthBySetPos" , function() {
	rruleStr();
});
rruleStr();
function rruleStr(){
	var x = RRule.fromString(createRruleStr());
	$("#rruleStr").text = x.toText();
}

/*
TODO: a better way to create the rrule_str, would probably to do something like "rruleByDay = getByDay(); if(rruleByDay){ //do stuff }"
Also get the yearly stuff done.


*/