/*
 * Handles all actions for studentis: showing them the current question and
 * letting them answer it.
 *
 * Note: This can later easily be refactored to also ask for ratings and stuff.
 *       Just alter has_new_question to has_new_action or something...
 */

var has_active_question = false;
var active_question_id;
var query_interval = 1000 * 5; // Every 5 sec
var query_interval_id;

$(function() {
    $("#answerform").submit(submit_answer);
    query_new_question();

	$('#answerform #counter').countdown({until: new Date(),
                                         compact: true,
                                         onExpiry: submit_answer});
    if (!has_active_question)
        query_interval_id = setInterval(query_new_question, query_interval);
});

function query_new_question() {
    if (has_active_question) {
        clearInterval(query_interval_id);
        return;
    }
    $.getJSON("/has_new_question", {},
        function(data) {
            if (data.has_new) {
                show_question(data.question_id, data.question_text,
                    data.time_remaining);
            }
			else {
				/* Poll for reviewable questions */
				$.getJSON("/has_new_review", {},
				function(data) {
					if (data.has_new) {
						show_review_button();
					}
					else {
						hide_review_button();
					}            
				});
			}
        });
}

function show_review_button() {
    console.log("GOT REVIEW");
	$('#reviewform #review-answer').val('You have a reviewable answer waiting for you!');
	$('#reviewform').show();
}

function hide_review_buttion(){
	$('#reviewform').hide();
}


function show_question(id, question, time_remaining) {
    console.log("GOT QUESTION", id, question, time_remaining);
    clearInterval(query_interval_id);
    has_active_question = true;
    active_question_id = id;
	var austDay = new Date();
	austDay.setSeconds(austDay.getSeconds() + time_remaining);
    console.log(austDay);
	$('#answerform #counter').countdown('option', {until: austDay,
                                         compact: true,
                                         onExpiry: submit_answer});

    $('#pleasewait').hide();
    $('#answerform #question').text(question);
    $('#answerform textarea').val('');
    $('#answerform').show();
}

function submit_answer() {
    console.log("SUBMIT");
    has_active_question = false;
    $('#pleasewait').show();
    $('#answerform').hide();

    $.post("/answer", {"questionID": active_question_id,
                       "answerText": $('#answerform textarea').val()});

    query_new_question();
    if (!has_active_question)
        query_interval_id = setInterval(query_new_question, query_interval);
    return false;
}
