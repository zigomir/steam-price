$('#subscribeButton').prop('disabled', true);
$('.integer').numeric(false);

var price_now = 0;

$('#subscribeForm').validate({
    submitHandler: function(form) {
        // custom validation
        if (price_now < $('#price').val()) {
            $('#message').text('Price already lower than ' + $('#price').val() + $('#currency_sign').text());
        } else {
            ajaxSubmit();
        }
    }
});

function ajaxSubmit() {
    $('#message').text('');
    
    $.post('/subscribe', 
        $('#subscribeForm').serialize(), 
        function(data) {
            console.log(data);
            if (data === 's') {
                $('#message').text('Subscription recieved. You will recieve an email when price is lower than ' + $('#price').val() + $('#currency_sign').text());
                $('#subscribeButton').prop('disabled', true);
                
                // clear form
                $(':input','#subscribeForm').not(':submit').val('');
                $('#steam_app_title').text('');
            }
        }, 
        'text');
}


$('#steam_app_id').change(function(){
    $('#subscribeButton').prop('disabled', true);
    $('#steam_app_title').text('');
    $('#message').text('');
    
    var steam_app_id = $(this).val();
    if (steam_app_id.length > 0) {
        $('#animation').show();
        ajaxGetAppTitle(steam_app_id);
    }
});

function ajaxGetAppTitle(steam_app_id) {
    $.get('/app_title/' + steam_app_id, 
        function(data) {
            if(data['title'] != 'null') {
                $('#subscribeButton').prop('disabled', false);
                $('#steam_app_title').text(data['title'] + ' (' + data['price_with_currency'] + ')');
                $('#currency_sign').text(data['currency_sign']);
                
                // for input value
                $('#steam_app_title_input').val(data['title']);
                $('#price_with_currency').val(data['price_with_currency']);
                
                // extra validation
                price_now = data['price'];
            } else {
                $('#steam_app_title').text('No game with this ID');
                $('#steam_app_title_input').val('');
            }
            $('#animation').hide();
        }, 
        'json');
}