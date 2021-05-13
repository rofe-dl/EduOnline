$(document).on('submit', '.give-exam-form', function(event){
    event.preventDefault();
    let questionForm = $(this);

    let posting = $.post(questionForm.attr('action'), questionForm.serialize());
    posting.done(function(){
        questionForm.find(".submit-question-btn").prop('disabled', true);
    })
})

$(document).on('change', '.exam-toggle', function(event){
    event.preventDefault();
    checkboxForm = $(this).closest('form');

    $.post(checkboxForm.attr('action'), checkboxForm.serialize());
})