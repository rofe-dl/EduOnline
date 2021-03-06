/**
     * Checks if the input fields like statement, mark and choice of a question form is empty or not
     * If empty, submit button of that form is greyed out
     * 
     * @param {Form} questionForm : The question form it will act on
     */
 function checkEmptyFields(questionForm){
    var empty = false;
    
    questionForm.find('input').each(function() {
        if ($(this).val() == '') {
            empty = true;
        }
    });

    // if no option is selected
    if (! questionForm.find("input[type=radio]:checked").val()) {
        empty = true;
    }

    if (empty) {
        questionForm.find('.submit-question-btn').prop('disabled', true);
    }else {
        questionForm.find('.submit-question-btn').prop('disabled', false);
    }
}

/**
 * Sets the value of every radio option in the question form 
 * to the value of the text field beside it.
 * 
 * @param {Form} questionForm : The question form it will act on
 */
 function setRadioValues(questionForm){

    questionForm.find('input[type=radio]').each(function(){
        let radio = $(this);
        radio.val(radio.closest(".choice-div").find("input[type=text]").val());
    })
}

/**
 * If any field on question form is edited, it'll check if
 * there's any empty input fields in the form
*/
$(document).on('keyup', 'form input[type=text], form input[type=number]', function(){
    checkEmptyFields($(this).closest('form'));
});

/**
 * If any of the choices of a question are selected, it'll check if
 * there's any empty input fields in the form
*/
$(document).on('click', '.empty-question-form input[type=radio], .filled-question-form input[type=radio]', function(){
    checkEmptyFields($(this).closest('form'));
});


/**
 * When a new question form submitted, values are assigned to radio buttons and
 * form is submitted.
 * 
 * I didn't find a way to input the question.id of the newly created question into the django
 * templated action={ url } of empty form so you can't edit the question you just added 
 * in the same page, you have to go the edit screen again. 
*/
$(document).on('submit', '.empty-question-form', function(event){
    event.preventDefault();
    var questionForm = $(this);
    setRadioValues(questionForm);
    
    var posting = $.post(questionForm.attr('action'), questionForm.serialize());

    posting.done(function(){
        questionForm.find(".submit-question-btn").prop('disabled', true);
        questionForm.find(".remove-question-btn").prop('disabled', true);
        questionForm.find(".add-choice-btn").prop('disabled', true);
    })
})

// .filled-question-form has two submit buttons, one to confirm and one to remove
// Both are handled differently in two separate functions below
// Both functions below deal with the submit buttons of already existing questions
$(document).on('click', '.filled-question-form .submit-question-btn', function(event){
    event.preventDefault();
    let questionForm = $(this).closest(".filled-question-form");
    setRadioValues(questionForm);

    // to pass name of the button that was clicked to the action url
    let dataArray = questionForm.serializeArray()
    dataArray.push({
        name: "submit_question",
        value: ""
    })

    let posting = $.post(questionForm.attr('action'), jQuery.param(dataArray) );
})

$(document).on('click', '.filled-question-form .remove-question-btn', function(event){
    event.preventDefault();
    let questionForm = $(this).closest(".filled-question-form");

    let dataArray = questionForm.serializeArray()
    dataArray.push({
        name: "remove_question",
        value: ""
    })

    let posting = $.post(questionForm.attr('action'), jQuery.param(dataArray) );

    posting.done(function(){
        questionForm.remove();
    })
    
})

$("#create-question-btn").click(function() {
    $(".questions-div").append($("#empty-question").html());
})

//didn't use just .click as above because elements are dynamically generated and may not exist when script runs
$(document).on('click', '.add-choice-btn', function(){ 
    $(this).closest("form").find('.choices').append($('#empty-choice').html());
    // new choice input will be empty, so submit buttong greyed out 
    $(this).closest('form').find('.submit-question-btn').prop('disabled', true);
})

$(document).on('click', '.remove-choice-btn', function(){
    questionForm = $(this).closest('form');
    $(this).closest(".choice-div").remove();
    checkEmptyFields(questionForm);
})

// only works on .empty-question-form, i.e the newly created questions
$(document).on('click', '.empty-question-form .remove-question-btn', function(){
    $(this).closest("form").remove();
})
